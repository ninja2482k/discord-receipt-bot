"""
Main entry point for the Discord Bot.

This script initializes the bot, loads configurations, sets up necessary intents,
registers slash commands, defines event handlers (like on_ready), and runs the bot.
It leverages other modules for specific functionalities:
- `config_loader.py`: For loading JSON configurations.
- `bot_commands.py`: For defining and registering slash commands.
- `email_utils.py`: For email sending functionalities.
"""

# Standard library imports
import os
import time
from typing import Dict # For bot.temp_order_data type hint
import asyncio
import sys

# Third-party imports
import discord
from discord.ext import commands
import dotenv

# Local module imports
from config_loader import load_config, load_email_template
from bot_commands import setup_commands, BotConfig
from email_utils import EmailService # Corrected import path

# --- Environment Variable Loading ---
dotenv.load_dotenv()

# --- Configuration Loading ---
config = load_config()
email_template = load_email_template()

# --- Bot Configuration & Credentials ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not BOT_TOKEN:
    print("CRITICAL ERROR: DISCORD_BOT_TOKEN not found in environment variables.")
    sys.exit(1)

# Optional: Add early check for SENDER_EMAIL and SENDER_PASSWORD if desired,
# but main_async will perform the critical check before EmailService initialization.
# if not SENDER_EMAIL or not SENDER_PASSWORD:
#     print("WARNING: SENDER_EMAIL or SENDER_PASSWORD not found. Email functionality will be unavailable.")

# --- Bot Initialization ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Bot State Variables ---
START_TIME = time.time()
bot.temp_order_data: Dict = {}

# --- Discord Bot Events ---
@bot.event
async def on_ready():
    """
    Event handler called when the bot has successfully connected to Discord,
    finished preparations, and is ready to operate.
    """
    print("-" * 50)
    print(f"🎉 Bot logged in as {bot.user.name} (ID: {bot.user.id})")
    print(f"⏱️ Current Bot Latency: {round(bot.latency * 1000)}ms")
    print(f"🌐 Bot is currently active in {len(bot.guilds)} server(s):")
    if bot.guilds:
        for guild in bot.guilds: # Simplified loop
            print(f"  - {guild.name} (ID: {guild.id})")
    else:
        print("  Bot is not in any servers.")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s) with Discord.")
    except discord.errors.Forbidden:
        print("⚠️ Error syncing commands: Bot lacks 'applications.commands' scope or permissions.")
    except Exception as e:
        print(f"⚠️ An unexpected error occurred while syncing slash commands: {e}")
    print("-" * 50)

async def main_async():
    """
    Main asynchronous function to setup and run the bot including EmailService.
    """
    email_service = None  # Initialize for finally block
    try:
        # SMTP Configuration
        smtp_host = config.get("smtp_server", "smtp.gmail.com")
        smtp_port_str = config.get("smtp_port", "587")
        try:
            smtp_port = int(smtp_port_str)
        except ValueError:
            print(f"CRITICAL: Invalid SMTP port '{smtp_port_str}'. Must be an integer.")
            sys.exit(1)

        if not SENDER_EMAIL or not SENDER_PASSWORD:
            print("CRITICAL: SENDER_EMAIL or SENDER_PASSWORD environment variables missing.")
            sys.exit(1)

        email_service = EmailService(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        print("Attempting to connect EmailService...")
        await email_service.connect() # Critical step, can raise exceptions
        print("✅ EmailService connected successfully.")

        # Update BotConfig instantiation (anticipates BotConfig class changes)
        bot_config_instance = BotConfig(
            start_time=START_TIME,
            email_service=email_service, # Pass EmailService instance
            email_template=email_template,
            app_config=config
        )

        print("Initializing and setting up slash commands...")
        setup_commands(bot, bot_config_instance)

        print("🚀 Attempting to connect to Discord...")
        await bot.start(BOT_TOKEN)

    except discord.errors.LoginFailure:
        print("❌ LOGIN FAILED: Check bot token (DISCORD_BOT_TOKEN).")
    except ConnectionRefusedError: # More specific for email service
        print(f"❌ CRITICAL: EmailService connection refused. Verify SMTP server ({smtp_host}:{smtp_port}) and network.")
    except aiosmtplib.SMTPConnectTimeoutError: # Specific timeout error
        print(f"❌ CRITICAL: EmailService connection timed out to {smtp_host}:{smtp_port}.")
    except aiosmtplib.SMTPAuthenticationError: # Specific auth error
        print(f"❌ CRITICAL: EmailService authentication failed for user {SENDER_EMAIL}.")
    except Exception as e:
        print(f"❌ An unexpected error occurred during bot setup or execution: {e}")
        # For detailed debugging, especially during development:
        import traceback
        traceback.print_exc()
    finally:
        print("🔌 Shutting down...")
        if email_service:
            print("Attempting to close EmailService connection...")
            await email_service.close()
            print("EmailService connection closed.")

        if hasattr(bot, 'is_closed') and not bot.is_closed():
            print("Attempting to close Discord bot connection...")
            await bot.close()
            print("Discord bot connection closed.")

# --- Run the Bot ---
if __name__ == "__main__":
    # Env vars and configs are loaded globally at the start of the script.
    # Critical checks for BOT_TOKEN are already performed.
    # SENDER_EMAIL and SENDER_PASSWORD will be checked in main_async.

    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nBot shutdown requested via KeyboardInterrupt.")
    finally:
        print("Bot script finished.")