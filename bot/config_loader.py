# bot/config_loader.py - Enhanced Configuration Management

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import aiofiles
from dataclasses import dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class SMTPConfig:
    """SMTP configuration data class."""
    server: str = "smtp.gmail.com"
    port: int = 587
    use_tls: bool = True
    timeout: int = 30

@dataclass
class EmailTemplate:
    """Email template configuration."""
    subject: str = "Order Confirmation - Receipt Bot"
    html_body: str = ""
    text_body: str = ""
    sender_name: str = "Receipt Bot"

@dataclass
class BotConfig:
    """Bot configuration data class."""
    command_prefix: str = "!"
    max_order_age_hours: int = 24
    max_concurrent_orders: int = 100
    rate_limit_per_minute: int = 5
    enable_logging: bool = True
    log_level: str = "INFO"
    database_url: Optional[str] = None

class ConfigLoader:
    """Enhanced configuration loader with caching and validation."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration caches
        self._smtp_config: Optional[SMTPConfig] = None
        self._email_template: Optional[EmailTemplate] = None
        self._bot_config: Optional[BotConfig] = None
        self._config_loaded = False
        
        # File paths
        self.config_file = self.config_dir / "config.json"
        self.email_template_file = self.config_dir / "email_template.json"
        self.bot_config_file = self.config_dir / "bot_config.json"
    
    async def load_config(self) -> None:
        """Load all configuration files."""
        if self._config_loaded:
            return
        
        try:
            # Load environment variables
            load_dotenv()
            
            # Load configuration files
            await self._load_smtp_config()
            await self._load_email_template()
            await self._load_bot_config()
            
            self._config_loaded = True
            logger.info("All configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    async def _load_smtp_config(self) -> None:
        """Load SMTP configuration."""
        try:
            if self.config_file.exists():
                async with aiofiles.open(self.config_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    self._smtp_config = SMTPConfig(
                        server=data.get('smtp_server', 'smtp.gmail.com'),
                        port=data.get('smtp_port', 587),
                        use_tls=data.get('smtp_use_tls', True),
                        timeout=data.get('smtp_timeout', 30)
                    )
            else:
                # Create default config
                self._smtp_config = SMTPConfig()
                await self._save_default_config()
                
        except Exception as e:
            logger.warning(f"Error loading SMTP config: {e}. Using defaults.")
            self._smtp_config = SMTPConfig()
    
    async def _load_email_template(self) -> None:
        """Load email template configuration."""
        try:
            if self.email_template_file.exists():
                async with aiofiles.open(self.email_template_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    self._email_template = EmailTemplate(
                        subject=data.get('subject', 'Order Confirmation - Receipt Bot'),
                        html_body=data.get('html_body', self._get_default_html_template()),
                        text_body=data.get('text_body', self._get_default_text_template()),
                        sender_name=data.get('sender_name', 'Receipt Bot')
                    )
            else:
                # Create default template
                self._email_template = EmailTemplate(
                    html_body=self._get_default_html_template(),
                    text_body=self._get_default_text_template()
                )
                await self._save_default_email_template()
                
        except Exception as e:
            logger.warning(f"Error loading email template: {e}. Using defaults.")
            self._email_template = EmailTemplate(
                html_body=self._get_default_html_template(),
                text_body=self._get_default_text_template()
            )
    
    async def _load_bot_config(self) -> None:
        """Load bot-specific configuration."""
        try:
            if self.bot_config_file.exists():
                async with aiofiles.open(self.bot_config_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    self._bot_config = BotConfig(
                        command_prefix=data.get('command_prefix', '!'),
                        max_order_age_hours=data.get('max_order_age_hours', 24),
                        max_concurrent_orders=data.get('max_concurrent_orders', 100),
                        rate_limit_per_minute=data.get('rate_limit_per_minute', 5),
                        enable_logging=data.get('enable_logging', True),
                        log_level=data.get('log_level', 'INFO'),
                        database_url=data.get('database_url')
                    )
            else:
                # Create default config
                self._bot_config = BotConfig()
                await self._save_default_bot_config()
                
        except Exception as e:
            logger.warning(f"Error loading bot config: {e}. Using defaults.")
            self._bot_config = BotConfig()
    
    async def _save_default_config(self) -> None:
        """Save default SMTP configuration."""
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_use_tls": True,
            "smtp_timeout": 30
        }
        
        async with aiofiles.open(self.config_file, 'w') as f:
            await f.write(json.dumps(default_config, indent=4))
        
        logger.info(f"Created default config file: {self.config_file}")
    
    async def _save_default_email_template(self) -> None:
        """Save default email template."""
        default_template = {
            "subject": "Order Confirmation - Receipt Bot",
            "sender_name": "Receipt Bot",
            "html_body": self._get_default_html_template(),
            "text_body": self._get_default_text_template()
        }
        
        async with aiofiles.open(self.email_template_file, 'w') as f:
            await f.write(json.dumps(default_template, indent=4))
        
        logger.info(f"Created default email template: {self.email_template_file}")
    
    async def _save_default_bot_config(self) -> None:
        """Save default bot configuration."""
        default_config = {
            "command_prefix": "!",
            "max_order_age_hours": 24,
            "max_concurrent_orders": 100,
            "rate_limit_per_minute": 5,
            "enable_logging": True,
            "log_level": "INFO",
            "database_url": null
        }
        
        async with aiofiles.open(self.bot_config_file, 'w') as f:
            await f.write(json.dumps(default_config, indent=4))
        
        logger.info(f"Created default bot config: {self.bot_config_file}")
    
    def _get_default_html_template(self) -> str:
        """Get default HTML email template."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Order Confirmation</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                .header { background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; margin: -20px -20px 20px -20px; }
                .order-details { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
                .highlight { color: #007bff; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧾 Order Confirmation</h1>
                    <p>Thank you for your order!</p>
                </div>
                
                <p>Hello <span class="highlight">{{customer_name}}</span>,</p>
                
                <p>We've received your order and it's being processed. Here are the details:</p>
                
                <div class="order-details">
                    <h3>📦 Order Details</h3>
                    <p><strong>Product:</strong> {{product_name}}</p>
                    <p><strong>Quantity:</strong> {{quantity}}</p>
                    <p><strong>Price:</strong> ${{price}}</p>
                    <p><strong>Order Date:</strong> {{order_date}}</p>
                    <p><strong>Order ID:</strong> {{order_id}}</p>
                </div>
                
                <p>If you have any questions about your order, please don't hesitate to contact us.</p>
                
                <div class="footer">
                    <p>This is an automated message from Receipt Bot</p>
                    <p>Powered by Enhanced Discord Receipt Bot</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_default_text_template(self) -> str:
        """Get default text email template."""
        return """
        ORDER CONFIRMATION
        
        Hello {{customer_name}},
        
        Thank you for your order! Here are the details:
        
        Order Details:
        - Product: {{product_name}}
        - Quantity: {{quantity}}
        - Price: ${{price}}
        - Order Date: {{order_date}}
        - Order ID: {{order_id}}
        
        If you have any questions, please contact us.
        
        Best regards,
        Receipt Bot Team
        
        ---
        This is an automated message from Receipt Bot
        """
    
    @property
    def smtp_config(self) -> SMTPConfig:
        """Get SMTP configuration."""
        if not self._config_loaded:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self._smtp_config
    
    @property
    def email_template(self) -> EmailTemplate:
        """Get email template configuration."""
        if not self._config_loaded:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self._email_template
    
    @property
    def bot_config(self) -> BotConfig:
        """Get bot configuration."""
        if not self._config_loaded:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self._bot_config
    
    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default."""
        return os.getenv(key, default)
    
    def get_required_env_var(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' not found")
        return value
    
    async def reload_config(self) -> None:
        """Reload all configuration files."""
        self._config_loaded = False
        self._smtp_config = None
        self._email_template = None
        self._bot_config = None
        await self.load_config()
        logger.info("Configuration reloaded successfully")
