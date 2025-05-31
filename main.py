"""
Main entry point for the Discord Bot.

This script initializes the bot, loads configurations, sets up necessary intents,
registers slash commands, defines event handlers (like on_ready), and runs the bot.
It leverages other modules for specific functionalities:
- `config_loader.py`: For loading JSON configurations.
- `bot_commands.py`: For defining and registering slash commands.
"""

# Standard library imports
import os
import time
from typing import Dict # For bot.temp_order_data type hint

# Third-party imports
import discord
from discord.ext import commands
import dotenv # For loading environment variables from .env file

# Local module imports
from config_loader import load_config, load_email_template
from bot_commands import setup_commands
# Note: `email_utils` and `discord_ui` are internally used by `bot_commands.py`
# and `discord_ui.py` respectively. They are not directly called from main.py after setup.

# --- Environment Variable Loading ---
# Load environment variables from a .env file for configuration.
# This should be one of the first things to do to ensure variables are available.
dotenv.load_dotenv()

# --- Configuration Loading ---
# Load application-specific configurations from JSON files.
# `config.json` typically holds general settings (e.g., SMTP server details).
# `email_template.json` holds the structure for emails sent by the bot.
config = load_config()
email_template = load_email_template()

# --- Bot Configuration & Credentials ---
# Load essential credentials and tokens from environment variables.
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Critical check: Ensure the bot token is available. Exit if not.
if not BOT_TOKEN:
    print("CRITICAL ERROR: DISCORD_BOT_TOKEN not found in environment variables.")
    print("Please ensure a .env file is present in the root directory with DISCORD_BOT_TOKEN set,")
    print("or that the environment variable is set in the deployment environment.")
import sys

    sys.exit(1) # Stop execution if token is missing

# --- Bot Initialization ---
# Define Discord intents required by the bot.
# `message_content` is an example; adjust intents based on your bot's specific needs
# to follow Discord's privileged intents policy.
intents = discord.Intents.default()
intents.message_content = True # Enabled if the bot needs to read message content (e.g. for prefix commands, though primarily using slash)
# intents.members = True      # Enable if the bot needs to track member joins/updates or access member lists exhaustively.
# intents.presences = True   # Enable if the bot needs to track user presence (status, activity).

# Create the bot instance with a command prefix (legacy, as primarily using slash commands)
# and specified intents. The command_prefix is still good practice to set.
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Bot State Variables ---
# START_TIME records when the bot script was initiated, used for uptime calculation in diagnostics.
START_TIME = time.time()

# bot.temp_order_data stores temporary data for multi-step interactions, such as modal forms.
# It's an in-memory dictionary. For persistent storage or larger scale applications,
# consider using a database (e.g., SQLite, PostgreSQL, Redis).
# Keyed by user_id, it holds data across different steps of a user's interaction with a form.
bot.temp_order_data: Dict = {}

# --- Setup Bot Commands ---
# Register all slash commands. These are defined in `bot_commands.py`.
# This call passes the bot instance and necessary global configurations (loaded earlier)
# to the command setup function, which then defines and registers the commands with the bot.
print("Initializing and setting up slash commands...")
setup_commands(
    bot,
    START_TIME,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    email_template,
    config
)

# --- Discord Bot Events ---
@bot.event
async def on_ready():
    """
    Event handler called when the bot has successfully connected to Discord,
    finished preparations, and is ready to operate.
    This event may be called multiple times if the bot disconnects and reconnects.
    """
    print("-" * 50)
    print(f"🎉 Bot logged in as {bot.user.name} (ID: {bot.user.id})")
    print(f"🔑 Successfully connected to Discord services.")
    print(f"⏱️ Current Bot Latency: {round(bot.latency * 1000)}ms")
    print(f"🌐 Bot is currently active in {len(bot.guilds)} server(s):")
    if bot.guilds:
        for guild_idx, guild in enumerate(bot.guilds):
            print(f"  {guild_idx+1}. {guild.name} (ID: {guild.id}) - Members: {guild.member_count if guild.member_count else 'N/A (check intents)'}")
    else:
        print("  Bot is not in any servers.")

    try:
        # Synchronize the application commands (slash commands) with Discord.
        # This is crucial for new or updated slash commands to appear for users.
        # For development, you might sync to a specific guild:
        # await bot.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))
        # For production, global sync is typical:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s) with Discord.")
    except discord.errors.Forbidden:
        print("⚠️ Error syncing slash commands: Bot lacks 'applications.commands' scope or permissions.")
        print("   Ensure the bot was invited with this scope and has necessary permissions in each server.")
    except Exception as e:
        print(f"⚠️ An unexpected error occurred while syncing slash commands: {e}")
    print("-" * 50)
    # Note on bot.temp_order_data:
    # This data currently persists across reconnects as it's an attribute of the bot object.
    # If it needed to be reset on each on_ready event (e.g., after a full restart vs. a simple reconnect),
    # one might re-initialize it here: `bot.temp_order_data = {}`.
    # However, for multi-step forms, persistence during a session (even with reconnects) is generally desired.

# --- Run the Bot ---
# This is the final step: start the bot using the loaded BOT_TOKEN.
# It's good practice to confirm the token was actually loaded before trying to run.
if BOT_TOKEN:
    print("🚀 Attempting to connect to Discord with the provided BOT_TOKEN...")
    try:
        bot.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("❌ LOGIN FAILED: Improper token has been passed.")
        print("   Please ensure the DISCORD_BOT_TOKEN in your .env file or environment is correct.")
    except Exception as e:
        print(f"❌ An unexpected error occurred while trying to run the bot: {e}")
else:
    # This case should ideally be caught by the earlier check, but as a fallback:
    print("❌ CRITICAL: Bot cannot run because DISCORD_BOT_TOKEN is missing.")

print("Bot script execution finished or interrupted.")