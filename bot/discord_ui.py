import discord
from discord.ext import commands

# --- Helper function for creating TextInput ---
def create_text_input(
    label: str,
    style: discord.TextStyle,
    required: bool,
    placeholder: str = None,
    default: str = None,
    max_length: int = None
) -> discord.ui.TextInput:
    """
    Creates a discord.ui.TextInput component with specified parameters.

    This helper function simplifies the creation of text input fields for modals
    by providing a clear and concise way to define their properties.

    Args:
        label (str): The label displayed above the text input field.
        style (discord.TextStyle): The style of the text input (e.g., short, paragraph).
        required (bool): Whether the field must be filled by the user.
        placeholder (str, optional): Placeholder text displayed in the empty field. Defaults to None.
        default (str, optional): Default text pre-filled in the field. Defaults to None.
        max_length (int, optional): Maximum number of characters allowed. Defaults to None.

    Returns:
        discord.ui.TextInput: The configured TextInput component.
    """
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
    """
    First step in the multi-step order form.
    Collects initial order details from the user.
    Upon submission, it passes the collected data and necessary configurations
    to the next step (OrderFormStep2) via a button callback.
    """
    def __init__(self, user_email: str, bot_instance: commands.Bot, send_email_func, cfg_sender_email: str, cfg_sender_password: str, cfg_email_template: dict, cfg_app_config: dict):
        """
        Initializes OrderFormStep1.

        Args:
            user_email (str): The email address of the user initiating the order.
            bot_instance (commands.Bot): The instance of the Discord bot (commands.Bot), used to access shared data like temp_order_data.
            send_email_func (callable): The asynchronous function used to send emails.
            cfg_sender_email (str): Sender's email address.
            cfg_sender_password (str): Sender's email password.
            cfg_email_template (dict): Email template data.
            cfg_app_config (dict): Application configuration (e.g., SMTP settings).
        """
        super().__init__()
        self.user_email = user_email
        self.bot_instance = bot_instance
        self.send_email_func = send_email_func
        self.sender_email = cfg_sender_email
        self.sender_password = cfg_sender_password
        self.email_template = cfg_email_template
        self.app_config = cfg_app_config

        self.form_fields: dict = {}
        """Stores references to the TextInput components added to the modal, keyed by their logical field names."""
        input_fields = {
            "order_number": ("Order Number", discord.TextStyle.short, True),
            "estimated_arrival_start_date": ("Arrival Start", discord.TextStyle.short, True),
            "estimated_arrival_end_date": ("Arrival End", discord.TextStyle.short, True),
            "product_image_url": ("Image URL", discord.TextStyle.short, True),
            "product_name": ("Product Name", discord.TextStyle.short, True),
        }

        for field_key, (label, style, required) in input_fields.items():
            input_component = create_text_input(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles the submission of OrderFormStep1.
        Stores the collected data in the bot's temporary storage and
        sends a message with a button to proceed to OrderFormStep2.
        The necessary configurations for email sending are passed along.
        """
        user_id = interaction.user.id
        user_data = {key: field.value for key, field in self.form_fields.items()}

        # Access temp_order_data through the bot_instance
        self.bot_instance.temp_order_data[user_id] = {
            'email': self.user_email,
            'step1_data': user_data
        }

        view = discord.ui.View()
        button = discord.ui.Button(label="Continue to Step 2", style=discord.ButtonStyle.primary, custom_id="continue_order_step2")

        async def button_callback(button_interaction: discord.Interaction):
            # Pass all necessary data to OrderFormStep2
            await button_interaction.response.send_modal(
                OrderFormStep2(
                    user_email=self.user_email,
                    user_id=user_id,
                    bot_instance=self.bot_instance, # or button_interaction.client
                    send_email_func=self.send_email_func,
                    cfg_sender_email=self.sender_email,
                    cfg_sender_password=self.sender_password,
                    cfg_email_template=self.email_template,
                    cfg_app_config=self.app_config
                )
            )

        button.callback = button_callback
        view.add_item(button)

        await interaction.response.send_message("Step 1 completed! Click below to continue:", view=view, ephemeral=True)

class OrderFormStep2(discord.ui.Modal, title="Order Details - Step 2"):
    """
    Second step in the multi-step order form.
    Collects further product details.
    """
    def __init__(self, user_email: str, user_id: int, bot_instance: commands.Bot, send_email_func, cfg_sender_email: str, cfg_sender_password: str, cfg_email_template: dict, cfg_app_config: dict):
        """
        Initializes OrderFormStep2.

        Args:
            user_email (str): The email address of the user.
            user_id (int): The Discord user ID.
            bot_instance (commands.Bot): The instance of the Discord bot.
            send_email_func (callable): The asynchronous function used to send emails.
            cfg_sender_email (str): Sender's email address.
            cfg_sender_password (str): Sender's email password.
            cfg_email_template (dict): Email template data.
            cfg_app_config (dict): Application configuration.
        """
        super().__init__()
        self.user_email = user_email
        self.user_id = user_id
        self.bot_instance = bot_instance
        self.send_email_func = send_email_func
        self.sender_email = cfg_sender_email
        self.sender_password = cfg_sender_password
        self.email_template = cfg_email_template
        self.app_config = cfg_app_config

        # Retrieve step1_data using bot_instance
        self.step1_data = self.bot_instance.temp_order_data[self.user_id]['step1_data']
        self.form_fields: dict = {}
        """Stores references to the TextInput components added to the modal, keyed by their logical field names."""
        input_fields = {
            "style_id": ("Style ID", discord.TextStyle.short, True),
            "product_size": ("Product Size", discord.TextStyle.short, True),
            "product_condition": ("Condition", discord.TextStyle.short, True),
            "purchase_price": ("Purchase Price", discord.TextStyle.short, True),
            "color": ("Color", discord.TextStyle.short, True),
        }

        for field_key, (label, style, required) in input_fields.items():
            input_component = create_text_input(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles the submission of OrderFormStep2.
        Stores the collected data and presents a button to proceed to OrderFormStep3.
        """
        step2_data = {key: field.value for key, field in self.form_fields.items()}
        self.bot_instance.temp_order_data[self.user_id]['step2_data'] = step2_data

        view = discord.ui.View()
        button = discord.ui.Button(label="Continue to Final Step", style=discord.ButtonStyle.primary, custom_id="continue_order_final")

        async def button_callback(button_interaction: discord.Interaction):
            await button_interaction.response.send_modal(
                OrderFormStep3(
                    user_email=self.user_email,
                    user_id=self.user_id,
                    bot_instance=self.bot_instance, # or button_interaction.client
                    send_email_func=self.send_email_func,
                    cfg_sender_email=self.sender_email,
                    cfg_sender_password=self.sender_password,
                    cfg_email_template=self.email_template,
                    cfg_app_config=self.app_config
                )
            )

        button.callback = button_callback
        view.add_item(button)

        await interaction.response.send_message("Step 2 completed! Click below to continue:", view=view, ephemeral=True)

class OrderFormStep3(discord.ui.Modal, title="Order Details - Step 3"):
    """
    Final step in the multi-step order form.
    Collects shipping information and additional notes.
    Upon submission, it consolidates all data, sends a confirmation email,
    and cleans up temporary user data.
    """
    def __init__(self, user_email: str, user_id: int, bot_instance: commands.Bot, send_email_func, cfg_sender_email: str, cfg_sender_password: str, cfg_email_template: dict, cfg_app_config: dict):
        """
        Initializes OrderFormStep3.

        Args:
            user_email (str): The email address of the user.
            user_id (int): The Discord user ID.
            bot_instance (commands.Bot): The instance of the Discord bot.
            send_email_func (callable): The asynchronous function used to send emails.
            cfg_sender_email (str): Sender's email address.
            cfg_sender_password (str): Sender's email password.
            cfg_email_template (dict): Email template data.
            cfg_app_config (dict): Application configuration.
        """
        super().__init__()
        self.user_email = user_email
        self.user_id = user_id
        self.bot_instance = bot_instance
        self.send_email_func = send_email_func
        self.sender_email = cfg_sender_email
        self.sender_password = cfg_sender_password
        self.email_template = cfg_email_template
        self.app_config = cfg_app_config

        user_specific_data = self.bot_instance.temp_order_data[self.user_id]
        self.step1_data = user_specific_data['step1_data']
        self.step2_data = user_specific_data.get('step2_data', {})
        self.form_fields: dict = {}
        """Stores references to the TextInput components added to the modal, keyed by their logical field names."""
        input_fields = {
            "shipping_address": ("Shipping Address", discord.TextStyle.paragraph, True),
            "notes": ("Additional Notes", discord.TextStyle.paragraph, False),
        }

        for field_key, (label, style, required) in input_fields.items():
            input_component = create_text_input(label=label, style=style, required=required)
            self.form_fields[field_key] = input_component
            self.add_item(input_component)

    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles the submission of OrderFormStep3.
        Merges all collected data, sends a confirmation email using the provided
        send_email_func and configurations, displays a final confirmation message to the user,
        and cleans up the temporary data from bot_instance.temp_order_data.
        """
        final_step_data = {key: field.value for key, field in self.form_fields.items()}
        merged_data = {**self.step1_data, **self.step2_data, **final_step_data}

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
            ephemeral=False, # Send to channel
        )

        # Call the passed send_email_func with all necessary arguments
        await self.send_email_func(
            recipient_email=self.user_email,
            email_data=merged_data,
            sender_email_address=self.sender_email,
            sender_password_value=self.sender_password,
            email_template_data=self.email_template,
            smtp_config=self.app_config
        )

        try:
            del self.bot_instance.temp_order_data[self.user_id]
            print(f"Successfully deleted temporary data for user {self.user_id}")
        except KeyError:
            print(f"No temporary data found for user {self.user_id} to delete.")
        except AttributeError:
            print("Error: bot_instance does not have temp_order_data attribute or it's not a dict.")
