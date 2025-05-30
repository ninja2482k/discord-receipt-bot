import discord
from discord.ext import commands
import aiosmtplib
from aiosmtplib.errors import SMTPAuthenticationError, SMTPRecipientRefused, SMTPSenderRefused, SMTPDataError, SMTPServerDisconnected, SMTPHeloError, SMTPException, SMTPRecipientsRefused
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import re
import time
from typing import Dict
import os
import dotenv

dotenv.load_dotenv()

# --- Configuration Loading ---
def load_config(filename="config.json"):
    """Loads configuration data from a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)

def load_email_template(filename="email_template.json"):
    """Loads email template data from a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)

config = load_config()
email_template = load_email_template()

# --- Bot Configuration ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

START_TIME = time.time()  # Bot uptime tracking
bot.temp_order_data: Dict = {}

# --- Email Functionality ---
async def send_email(recipient_email, email_data): # Changed to async def
    """Sends an email with order details."""
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = recipient_email
    message['Subject'] = "Order Confirmation"

    html_body = email_template["html_body"]
    for key, value in email_data.items():
        html_body = html_body.replace(f"{{{{{key}}}}}", value)

    message.attach(MIMEText(html_body, 'html'))

    try:
        smtp_server_address = config.get("smtp_server", "smtp.gmail.com")
        smtp_port_number = config.get("smtp_port", 587)
        async with aiosmtplib.SMTP(hostname=smtp_server_address, port=smtp_port_number) as server:
            await server.starttls()
            await server.login(SENDER_EMAIL, SENDER_PASSWORD)
            await server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        print(f"Email sent to {recipient_email}")
    except SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error for {recipient_email}: {e}")
    except SMTPRecipientsRefused as e: # Handles multiple recipients refused
        print(f"All recipients refused for {recipient_email}: {e}")
    except SMTPRecipientRefused as e: # Handles single recipient refused
        print(f"Recipient refused for {recipient_email}: {e}")
    except SMTPSenderRefused as e:
        print(f"Sender refused for {recipient_email}: {e}")
    except SMTPDataError as e:
        print(f"SMTP Data Error for {recipient_email}: {e}")
    except SMTPServerDisconnected as e:
        print(f"SMTP Server disconnected for {recipient_email}: {e}")
    except SMTPHeloError as e:
        print(f"SMTP Helo Error for {recipient_email}: {e}")
    except SMTPException as e: # General aiosmtplib exception
        print(f"SMTP General Error for {recipient_email}: {e}")
    except Exception as error:
        print(f"Generic error sending email to {recipient_email}: {error}")

def is_valid_email(email):
    """Validates an email address using a regular expression."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

# --- Helper function for creating TextInput ---
def create_text_input(label: str, style: discord.TextStyle, required: bool, placeholder: str = None, default: str = None, max_length: int = None):
    return discord.ui.TextInput(
        label=label,
        style=style,
        required=required,
        placeholder=placeholder,
        default=default,
        max_length=max_length
    )

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
            # Use the helper function here
            input_component = create_text_input(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_data = {key: field.value for key, field in self.form_fields.items()}
        # Store the data in a temporary dictionary or database
        interaction.client.temp_order_data[user_id] = {
            'email': self.user_email,
            'step1_data': user_data
        }
        
        # Create continue button
        view = discord.ui.View()
        button = discord.ui.Button(label="Continue to Step 2", style=discord.ButtonStyle.primary, custom_id="continue_order")
        
        async def button_callback(button_interaction):
            # Pass user_id to OrderFormStep2
            await button_interaction.response.send_modal(OrderFormStep2(self.user_email, user_id))
            
        button.callback = button_callback
        view.add_item(button)
        
        await interaction.response.send_message("Step 1 completed! Click below to continue:", view=view, ephemeral=True)

class OrderFormStep2(discord.ui.Modal, title="Order Details - Step 2"):
    def __init__(self, user_email, user_id): # Accept user_id
        super().__init__()
        self.user_email = user_email
        self.user_id = user_id # Store user_id
        # Retrieve step1_data using user_id
        self.step1_data = bot.temp_order_data[self.user_id]['step1_data']
        self.form_fields = {}

        input_fields = {
            "style_id": ("Style ID", discord.TextStyle.short, True),
            "product_size": ("Product Size", discord.TextStyle.short, True),
            "product_condition": ("Condition", discord.TextStyle.short, True),
            "purchase_price": ("Purchase Price", discord.TextStyle.short, True),
            "color": ("Color", discord.TextStyle.short, True),
        }

        for field_key, (label, style, required) in input_fields.items():
            # Use the helper function here
            input_component = create_text_input(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        step2_data = {key: field.value for key, field in self.form_fields.items()}
        # Store updated data using user_id
        interaction.client.temp_order_data[self.user_id]['step2_data'] = step2_data
        
        # Create continue button for step 3
        view = discord.ui.View()
        button = discord.ui.Button(label="Continue to Final Step", style=discord.ButtonStyle.primary, custom_id="continue_final")
        
        async def button_callback(button_interaction):
            # Pass user_id to OrderFormStep3
            await button_interaction.response.send_modal(OrderFormStep3(self.user_email, self.user_id))
            
        button.callback = button_callback
        view.add_item(button)
        
        await interaction.response.send_message("Step 2 completed! Click below to continue:", view=view, ephemeral=True)

class OrderFormStep3(discord.ui.Modal, title="Order Details - Step 3"):
    def __init__(self, user_email, user_id): # Accept user_id
        super().__init__()
        self.user_email = user_email
        self.user_id = user_id # Store user_id
        # Retrieve data using user_id
        user_specific_data = bot.temp_order_data[self.user_id]
        self.step1_data = user_specific_data['step1_data']
        self.step2_data = user_specific_data.get('step2_data', {}) # Use .get for safety
        self.form_fields = {}

        input_fields = {
            "shipping_address": ("Shipping Address", discord.TextStyle.paragraph, True),
            "notes": ("Additional Notes", discord.TextStyle.paragraph, False),
        }

        for field_key, (label, style, required) in input_fields.items():
            # Use the helper function here
            input_component = create_text_input(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        final_step_data = {key: field.value for key, field in self.form_fields.items()}
        # Merge all data parts
        merged_data = {**self.step1_data, **self.step2_data, **final_step_data}

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
        await send_email(self.user_email, merged_data) # Added await here

        # Clean up user's data
        try:
            del interaction.client.temp_order_data[self.user_id]
            print(f"Successfully deleted data for user {self.user_id}")
        except KeyError:
            print(f"No data found for user {self.user_id} to delete.")

# --- Discord Bot Events & Commands ---
@bot.event
async def on_ready():
    print("🤖 Bot is online and ready!")
    await bot.tree.sync()

# @bot.command()
# async def ping(ctx):
#     """Responds with Pong! 🏓"""
#     await ctx.send("Pong! 🏓")

@bot.tree.command(name="ping", description="Responds with Pong! and bot latency.")
async def ping_slash(interaction: discord.Interaction):
    """Responds with Pong! and the bot's latency."""
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency_ms}ms")

@bot.tree.command(name="run_diagnostics", description="Check bot's status.")
async def run_diagnostics_command(interaction: discord.Interaction):
    uptime_seconds = time.time() - START_TIME
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    ping_ms = round(bot.latency * 1000)
    server_count = len(bot.guilds)
    user_count = sum(guild.member_count for guild in bot.guilds)

    diagnostics = (
        f"**Bot Diagnostics**\n"
        f"Ping: {ping_ms}ms\n"
        f"Uptime: {days}d {hours}h {minutes}m\n"
        f"Servers: {server_count}\n"
        f"Users: {user_count}\n"
    )
    await interaction.response.send_message(diagnostics)

@bot.tree.command(name="order_form", description="Open an order submission form.")
async def order_form_command(interaction: discord.Interaction, email: str):
    if not is_valid_email(email):
        await interaction.response.send_message("❌ Invalid email.", ephemeral=True)
        return
    await interaction.response.send_modal(OrderFormStep1(email))

# --- Run the Bot ---
bot.run(BOT_TOKEN)