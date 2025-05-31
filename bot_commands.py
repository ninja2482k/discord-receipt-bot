import discord
from discord.ext import commands # Required for commands.Bot type hint if used, and for bot.tree.command
import time
from email_utils import is_valid_email, send_email as email_util_send_email
from discord_ui import OrderFormStep1

# This file will contain the setup_commands function which defines and registers
# all slash commands for the bot. This helps in keeping main.py cleaner.

from dataclasses import dataclass

@dataclass
class BotConfig:
    """Configuration for bot setup."""
    start_time: float
    sender_email: str
    sender_password: str
    email_template: dict
    app_config: dict

def setup_commands(bot: commands.Bot, config: BotConfig):
    """
    Sets up and registers all slash commands for the bot.

    Args:
        bot (commands.Bot): The bot instance.
        config (BotConfig): Bot configuration including timing and email settings.
    """
    # ... rest of implementation ...
    @bot.tree.command(name="ping", description="Responds with Pong! and bot latency.")
    async def ping_slash(interaction: discord.Interaction):
        """
        Handles the /ping command.
        Responds with the bot's current latency.
        """
        latency_ms = round(bot.latency * 1000) # 'bot' is from the setup_commands scope
        await interaction.response.send_message(f"Pong! Latency: {latency_ms}ms")
        print(f"Ping command executed by {interaction.user.name} in guild {interaction.guild.name if interaction.guild else 'DM'}")

    @bot.tree.command(name="run_diagnostics", description="Check bot's status and diagnostic information.")
    async def run_diagnostics_command(interaction: discord.Interaction):
        """
        Handles the /run_diagnostics command.
        Provides diagnostic information about the bot like uptime, server count, user count, and latency.
        """
        # Calculate uptime
        uptime_seconds = time.time() - START_TIME # 'START_TIME' is from the setup_commands scope
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        # Get other diagnostics
        ping_ms = round(bot.latency * 1000) # 'bot' is from the setup_commands scope
        server_count = len(bot.guilds)
        user_count = 0
        for guild in bot.guilds:
            try:
                user_count += guild.member_count
            except AttributeError: # member_count might not be available in some partial guild objects or due to intent issues
                print(f"Warning: Could not retrieve member_count for guild {guild.id}. Ensure GUILD_MEMBERS intent is enabled if this is unexpected.")


        # Structure of the diagnostic message:
        # - Bot Ping (Latency)
        # - Uptime (Days, Hours, Minutes, Seconds)
        # - Number of Servers the bot is in
        # - Total number of Users the bot can see (sum of members in all servers)
        diagnostics = (
            f"**🤖 Bot Diagnostics**\n\n"
            f"**Ping:** {ping_ms}ms\n"
            f"**Uptime:** {days}d {hours}h {minutes}m {seconds}s\n"
            f"**Servers:** {server_count}\n"
            f"**Users (approximate):** {user_count}\n" # Clarified that user count can be approximate
        )
        await interaction.response.send_message(diagnostics, ephemeral=True) # Made ephemeral for cleaner channels
        print(f"Run_diagnostics command executed by {interaction.user.name}")

    @bot.tree.command(name="order_form", description="Open an order submission form.")
    async def order_form_command(interaction: discord.Interaction, email: str):
        """
        Handles the /order_form command.
        Validates the provided email and, if valid, initiates a multi-step order form modal sequence.

        Args:
            interaction (discord.Interaction): The interaction object from Discord.
            email (str): The email address provided by the user for the order.
        """
        if not is_valid_email(email): # is_valid_email is imported from email_utils
            await interaction.response.send_message("❌ Invalid email address provided. Please use a valid email format.", ephemeral=True)
            return

        # Instantiating the first step of the order form (OrderFormStep1).
        # This modal will then handle subsequent steps.
        # All necessary configurations (bot instance, email sending function, and email/app configs)
        # are passed to the modal. These will be propagated through the modal chain as needed.
        modal = OrderFormStep1(
            user_email=email,
            bot_instance=bot, # 'bot' is from the setup_commands scope
            send_email_func=email_util_send_email, # actual send_email function from email_utils
            cfg_sender_email=SENDER_EMAIL_CFG,
            cfg_sender_password=SENDER_PASSWORD_CFG,
            cfg_email_template=EMAIL_TEMPLATE_CFG,
            cfg_app_config=APP_CONFIG_CFG
        )
        await interaction.response.send_modal(modal)
        print(f"Order_form command initiated by {interaction.user.name} with email {email}")

    print("✅ Bot slash commands have been defined and attached to the bot's tree.")
    # The actual registration with Discord happens when bot.tree.sync() is called, typically in on_ready.
