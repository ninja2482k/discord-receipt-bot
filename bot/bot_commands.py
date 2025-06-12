import discord
from discord.ext import commands
import time
from .email_utils import is_valid_email, EmailService
from discord_ui import OrderFormStep1

from dataclasses import dataclass

@dataclass
class BotConfig:
    """Configuration for bot setup."""
    start_time: float
    email_service: EmailService
    email_template: dict
    app_config: dict

def setup_commands(bot: commands.Bot, config: BotConfig):
    """
    Sets up and registers all slash commands for the bot.

    Args:
        bot (commands.Bot): The bot instance.
        config (BotConfig): Bot configuration including timing, EmailService, and templates.
    """

    @bot.tree.command(name="ping", description="Responds with Pong! and bot latency.")
    async def ping_slash(interaction: discord.Interaction):
        latency_ms = round(bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency: {latency_ms}ms")
        print(f"Ping command executed by {interaction.user.name} in guild {interaction.guild.name if interaction.guild else 'DM'}")

    @bot.tree.command(name="run_diagnostics", description="Check bot's status and diagnostic information.")
    async def run_diagnostics_command(interaction: discord.Interaction):
        uptime_seconds = time.time() - config.start_time
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        ping_ms = round(bot.latency * 1000)
        server_count = len(bot.guilds)
        user_count = 0
        for guild in bot.guilds:
            try:
                user_count += guild.member_count
            except AttributeError:
                print(f"Warning: Could not retrieve member_count for guild {guild.id}.")

        diagnostics = (
            f"**🤖 Bot Diagnostics**\n\n"
            f"**Ping:** {ping_ms}ms\n"
            f"**Uptime:** {days}d {hours}h {minutes}m {seconds}s\n"
            f"**Servers:** {server_count}\n"
            f"**Users (approximate):** {user_count}\n"
        )
        await interaction.response.send_message(diagnostics, ephemeral=True)
        print(f"Run_diagnostics command executed by {interaction.user.name}")

    @bot.tree.command(name="order_form", description="Open an order submission form.")
    async def order_form_command(interaction: discord.Interaction, email: str):
        if not is_valid_email(email):
            await interaction.response.send_message("❌ Invalid email address provided. Please use a valid email format.", ephemeral=True)
            return

        # Instantiating OrderFormStep1, now passing the entire BotConfig object.
        # OrderFormStep1's __init__ in discord_ui.py will need to be updated
        # to accept bot_config_obj and access its attributes.
        modal = OrderFormStep1(
            user_email=email,
            bot_instance=bot, # Still passed directly for temp_order_data
            bot_config_obj=config # Pass the whole BotConfig object
        )
        await interaction.response.send_modal(modal)
        print(f"Order_form command initiated by {interaction.user.name} with email {email}")

    print("✅ Bot slash commands have been defined and attached to the bot's tree.")
    # Actual registration with Discord happens via bot.tree.sync() (typically in on_ready).
