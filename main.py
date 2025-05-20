import discord
from discord.ext import commands
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import re
import time
import logging
import os
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration Loading ---
def load_config(filename: str = "config.json") -> dict:
    """
    Loads configuration data from a JSON file.
    
    Args:
        filename (str): Path to the configuration file
        
    Returns:
        dict: Configuration data
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        json.JSONDecodeError: If the configuration file is invalid JSON
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file {filename} not found")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file {filename}")
        raise

def load_email_template(filename: str = "email_template.json") -> dict:
    """
    Loads email template data from a JSON file.
    
    Args:
        filename (str): Path to the email template file
        
    Returns:
        dict: Email template data
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Email template file {filename} not found")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in email template file {filename}")
        raise

# --- Environment and Configuration Setup ---
load_dotenv()  # Load environment variables from .env file

config = load_config()
email_template = load_email_template()

SENDER_EMAIL = os.getenv('SENDER_EMAIL') or config.get("email")
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') or config.get("email_password")
BOT_TOKEN = os.getenv('BOT_TOKEN') or config.get("bot_token")

if not all([SENDER_EMAIL, SENDER_PASSWORD, BOT_TOKEN]):
    logger.error("Missing required environment variables")
    raise EnvironmentError("Missing required environment variables")

# --- Bot Configuration ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

START_TIME = time.time()
bot.temp_order_data = {}

class EmailError(Exception):
    """Custom exception for email-related errors."""
    pass

# --- Email Functionality ---
def send_email(recipient_email: str, email_data: Dict) -> bool:
    """
    Sends an email with order details.
    
    Args:
        recipient_email (str): The recipient's email address
        email_data (Dict): Dictionary containing the email data
        
    Returns:
        bool: True if email was sent successfully, False otherwise
        
    Raises:
        EmailError: If there's an error sending the email
    """
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = recipient_email
    message['Subject'] = "Order Confirmation"

    html_body = email_template["html_body"]
    for key, value in email_data.items():
        html_body = html_body.replace(f"{{{{{key}}}}}", str(value))

    message.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as error:
        logger.error(f"Error sending email to {recipient_email}: {error}")
        raise EmailError(f"Failed to send email: {str(error)}")

def is_valid_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))

def validate_date_format(date_str: str) -> bool:
    """
    Validates if a date string is in the correct format (YYYY-MM-DD).
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if date format is valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# --- Discord UI Modals ---
class OrderFormStep1(discord.ui.Modal, title="Order Details - Step 1"):
    def __init__(self, user_email):
        super().__init__()
        self.user_email = user_email
        self.form_fields = {}

        input_fields = {
            "order_number": ("Order Number", discord.TextStyle.short, True),
            "estimated_arrival_start_date": ("Arrival Start", discord.TextStyle.short, True),
            "estimated_arrival_end_date": ("Arrival End", discord.TextStyle.short, True),
            "product_image_url": ("Image URL", discord.TextStyle.short, True),
            "product_name": ("Product Name", discord.TextStyle.short, True),
        }

        for field_key, (label, style, required) in input_fields.items():
            input_component = discord.ui.TextInput(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = {key: field.value for key, field in self.form_fields.items()}
        # Store the data in a temporary dictionary or database
        interaction.client.temp_order_data = {
            'email': self.user_email,
            'step1_data': user_data
        }
        
        # Create continue button
        view = discord.ui.View()
        button = discord.ui.Button(label="Continue to Step 2", style=discord.ButtonStyle.primary, custom_id="continue_order")
        
        async def button_callback(button_interaction):
            await button_interaction.response.send_modal(OrderFormStep2(self.user_email, user_data))
            
        button.callback = button_callback
        view.add_item(button)
        
        await interaction.response.send_message("Step 1 completed! Click below to continue:", view=view, ephemeral=True)

class OrderFormStep2(discord.ui.Modal, title="Order Details - Step 2"):
    def __init__(self, user_email, step1_data):
        super().__init__()
        self.user_email = user_email
        self.step1_data = step1_data
        self.form_fields = {}

        input_fields = {
            "style_id": ("Style ID", discord.TextStyle.short, True),
            "product_size": ("Product Size", discord.TextStyle.short, True),
            "product_condition": ("Condition", discord.TextStyle.short, True),
            "purchase_price": ("Purchase Price", discord.TextStyle.short, True),
            "color": ("Color", discord.TextStyle.short, True),
        }

        for field_key, (label, style, required) in input_fields.items():
            input_component = discord.ui.TextInput(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        step2_data = {key: field.value for key, field in self.form_fields.items()}
        temp_data = {**self.step1_data, **step2_data}
        
        # Store updated data
        interaction.client.temp_order_data.update({'step2_data': step2_data})
        
        # Create continue button for step 3
        view = discord.ui.View()
        button = discord.ui.Button(label="Continue to Final Step", style=discord.ButtonStyle.primary, custom_id="continue_final")
        
        async def button_callback(button_interaction):
            await button_interaction.response.send_modal(OrderFormStep3(self.user_email, temp_data))
            
        button.callback = button_callback
        view.add_item(button)
        
        await interaction.response.send_message("Step 2 completed! Click below to continue:", view=view, ephemeral=True)

class OrderFormStep3(discord.ui.Modal, title="Order Details - Step 3"):
    def __init__(self, user_email, previous_data):
        super().__init__()
        self.user_email = user_email
        self.previous_data = previous_data
        self.form_fields = {}

        input_fields = {
            "shipping_address": ("Shipping Address", discord.TextStyle.paragraph, True),
            "notes": ("Additional Notes", discord.TextStyle.paragraph, False),
        }

        for field_key, (label, style, required) in input_fields.items():
            input_component = discord.ui.TextInput(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        final_step_data = {key: field.value for key, field in self.form_fields.items()}
        merged_data = {**self.previous_data, **final_step_data}

        # Send final confirmation message
        await interaction.response.send_message(
            content=(
                f"✅ **Order Submitted!**\n\n"
                f"📦 **Product:** {merged_data['product_name']}\n"
                f"💰 **Total Paid:** {merged_data['purchase_price']}\n"
                f"🚚 **Estimated Arrival:** {merged_data['estimated_arrival_start_date']} to {merged_data['estimated_arrival_end_date']}\n"
                f"ℹ️ **Style ID:** {merged_data['style_id']}\n"
                f"📏 **Size:** {merged_data['product_size']}\n"
                f"🎨 **Color:** {merged_data['color']}\n"
                f"📜 **Condition:** {merged_data['product_condition']}\n"
                f"📍 **Shipping To:** {merged_data['shipping_address']}"
            ),
            ephemeral=False,
        )
        send_email(self.user_email, merged_data)

# --- Discord Bot Events & Commands ---
@bot.event
async def on_ready():
    """Handler for bot ready event."""
    logger.info(f"🤖 Bot is online as {bot.user.name}!")
    await bot.tree.sync()

@bot.event
async def on_error(event: str, *args, **kwargs):
    """Global error handler for the bot."""
    logger.error(f"Error in {event}: {args} {kwargs}")

@bot.tree.command(name="run_diagnostics", description="Check bot's status.")
async def run_diagnostics_command(interaction: discord.Interaction):
    """
    Command to check the bot's diagnostic information.
    
    Args:
        interaction (discord.Interaction): The interaction that triggered this command
    """
    try:
        uptime_seconds = time.time() - START_TIME
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)

        ping_ms = round(bot.latency * 1000)
        server_count = len(bot.guilds)
        user_count = sum(guild.member_count for guild in bot.guilds)
        
        memory_usage = os.popen('ps -o rss= -p %d' % os.getpid()).read()
        memory_mb = int(memory_usage) / 1024  # Convert KB to MB

        diagnostics = (
            f"**Bot Diagnostics**\n"
            f"🏓 Ping: {ping_ms}ms\n"
            f"⏱️ Uptime: {days}d {hours}h {minutes}m\n"
            f"🌐 Servers: {server_count}\n"
            f"👥 Users: {user_count}\n"
            f"💾 Memory Usage: {memory_mb:.1f} MB\n"
            f"🔄 Last Started: {datetime.fromtimestamp(START_TIME).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await interaction.response.send_message(diagnostics)
        logger.info("Diagnostics command executed successfully")
    except Exception as e:
        logger.error(f"Error in diagnostics command: {str(e)}")
        await interaction.response.send_message("❌ An error occurred while fetching diagnostics.", ephemeral=True)

@bot.tree.command(name="order_form", description="Open an order submission form.")
async def order_form_command(interaction: discord.Interaction, email: str):
    """
    Command to open the order submission form.
    
    Args:
        interaction (discord.Interaction): The interaction that triggered this command
        email (str): User's email address
    """
    try:
        if not is_valid_email(email):
            await interaction.response.send_message("❌ Please provide a valid email address.", ephemeral=True)
            return
        
        logger.info(f"Opening order form for user {interaction.user.id} with email {email}")
        await interaction.response.send_modal(OrderFormStep1(email))
    except Exception as e:
        logger.error(f"Error in order form command: {str(e)}")
        await interaction.response.send_message("❌ An error occurred while opening the order form.", ephemeral=True)

# --- Run the Bot ---
if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        bot.run(BOT_TOKEN)
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
        raise