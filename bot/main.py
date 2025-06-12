# bot/main.py - Enhanced Discord Receipt Bot with Performance Optimizations

import asyncio
import logging
import os
import sys
from typing import Optional
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import aiohttp
import time
from contextlib import asynccontextmanager

from config_loader import ConfigLoader
from bot_commands import setup_commands
from email_utils import EmailManager
from database_manager import DatabaseManager

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnhancedReceiptBot(commands.Bot):
    """Enhanced Discord Receipt Bot with improved performance and features."""
    
    def __init__(self):
        # Enhanced intents for better functionality
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # For member count diagnostics
        
        super().__init__(
            command_prefix='!',  # Fallback prefix, primarily using slash commands
            intents=intents,
            help_command=None,  # Custom help command
            case_insensitive=True,
            strip_after_prefix=True
        )
        
        # Bot state management
        self.start_time = time.time()
        self.order_data = {}  # Thread-safe order data storage
        self.rate_limit_buckets = {}  # Rate limiting
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Component managers
        self.config_loader = ConfigLoader()
        self.email_manager = None
        self.db_manager = None
        
        # Performance metrics
        self.command_usage = {}
        self.error_count = 0
        
    async def setup_hook(self):
        """Async setup called when bot starts."""
        try:
            # Load configuration
            await self.config_loader.load_config()
            logger.info("Configuration loaded successfully")
            
            # Initialize managers
            self.email_manager = EmailManager(self.config_loader)
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            # Create aiohttp session for external requests
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
            )
            
            # Setup commands
            await setup_commands(self)
            
            # Start background tasks
            self.cleanup_task.start()
            self.metrics_task.start()
            
            # Sync slash commands
            await self.tree.sync()
            logger.info("Slash commands synced successfully")
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
            raise
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        logger.info(f'Serving {sum(guild.member_count for guild in self.guilds)} users')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servers | /help"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Enhanced error handling."""
        self.error_count += 1
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, ephemeral=True)
            
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            
        elif isinstance(error, commands.CommandNotFound):
            # Silently ignore command not found errors
            pass
            
        else:
            logger.error(f"Unhandled error in command {ctx.command}: {error}")
            embed = discord.Embed(
                title="🚫 An Error Occurred",
                description="An unexpected error occurred. The development team has been notified.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
    
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Handle slash command errors."""
        self.error_count += 1
        
        if interaction.response.is_done():
            send_method = interaction.followup.send
        else:
            send_method = interaction.response.send_message
        
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
                color=discord.Color.orange()
            )
            await send_method(embed=embed, ephemeral=True)
        else:
            logger.error(f"Unhandled app command error: {error}")
            embed = discord.Embed(
                title="🚫 An Error Occurred",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await send_method(embed=embed, ephemeral=True)
    
    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Clean up old order data and perform maintenance."""
        try:
            current_time = time.time()
            # Remove order data older than 1 hour
            expired_orders = [
                user_id for user_id, data in self.order_data.items()
                if current_time - data.get('timestamp', 0) > 3600
            ]
            
            for user_id in expired_orders:
                del self.order_data[user_id]
            
            if expired_orders:
                logger.info(f"Cleaned up {len(expired_orders)} expired order sessions")
                
            # Clean up rate limit buckets
            self.rate_limit_buckets = {
                k: v for k, v in self.rate_limit_buckets.items()
                if current_time - v < 300  # 5 minutes
            }
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    @tasks.loop(minutes=30)
    async def metrics_task(self):
        """Update bot metrics and status."""
        try:
            total_users = sum(guild.member_count for guild in self.guilds)
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{len(self.guilds)} servers | {total_users} users"
                )
            )
        except Exception as e:
            logger.error(f"Error in metrics task: {e}")
    
    @cleanup_task.before_loop
    @metrics_task.before_loop
    async def wait_until_ready(self):
        """Wait until bot is ready before starting tasks."""
        await self.wait_until_ready()
    
    async def close(self):
        """Cleanup when bot shuts down."""
        logger.info("Bot is shutting down...")
        
        # Cancel tasks
        if hasattr(self, 'cleanup_task'):
            self.cleanup_task.cancel()
        if hasattr(self, 'metrics_task'):
            self.metrics_task.cancel()
        
        # Close aiohttp session
        if self.session:
            await self.session.close()
        
        # Close database connection
        if self.db_manager:
            await self.db_manager.close()
        
        await super().close()
        logger.info("Bot shutdown complete")
    
    def is_rate_limited(self, user_id: int, command: str, limit: int = 5, window: int = 60) -> bool:
        """Check if user is rate limited for a command."""
        current_time = time.time()
        key = f"{user_id}:{command}"
        
        if key not in self.rate_limit_buckets:
            self.rate_limit_buckets[key] = []
        
        # Remove old timestamps
        self.rate_limit_buckets[key] = [
            timestamp for timestamp in self.rate_limit_buckets[key]
            if current_time - timestamp < window
        ]
        
        # Check if limit exceeded
        if len(self.rate_limit_buckets[key]) >= limit:
            return True
        
        # Add current timestamp
        self.rate_limit_buckets[key].append(current_time)
        return False

@asynccontextmanager
async def get_bot():
    """Context manager for bot lifecycle."""
    bot = EnhancedReceiptBot()
    try:
        yield bot
    finally:
        await bot.close()

async def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['DISCORD_BOT_TOKEN', 'SENDER_EMAIL', 'SENDER_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    # Start the bot with proper error handling
    async with get_bot() as bot:
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.error("Invalid bot token provided")
            sys.exit(1)
        except discord.HTTPException as e:
            logger.error(f"HTTP error occurred: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Bot shutdown requested by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
