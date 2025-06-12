import discord
-from .bot_commands import BotConfig # Added import for BotConfig
+from bot.bot_commands import BotConfig # Added import for BotConfig

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
    """
    return discord.ui.TextInput(
        label=label,
        style=style,
        required=required,
        placeholder=placeholder,
        default=default,
        max_length=max_length
    )

# --- Helper function for Modal Transitions ---
async def _prepare_next_modal_step(
    interaction: discord.Interaction,
    current_modal,
    user_id: int,
    data_key_name: str,
    next_modal_class: type[discord.ui.Modal],
    button_label: str,
    confirmation_message: str
):
    """
    Handles common logic for transitioning to the next modal step.
    """
    user_data = {key: field.value for key, field in current_modal.form_fields.items()}

    if user_id not in current_modal.bot_instance.temp_order_data:
        current_modal.bot_instance.temp_order_data[user_id] = {'email': current_modal.user_email}
        print(f"Warning: Initialized temp_order_data for user_id {user_id} in _prepare_next_modal_step. This might be unexpected if not Step 1.")

    current_modal.bot_instance.temp_order_data[user_id][data_key_name] = user_data

    view = discord.ui.View()
    button = discord.ui.Button(label=button_label, style=discord.ButtonStyle.primary)

    async def button_callback(button_interaction: discord.Interaction):
        try: # Add try-except within button callback for modal instantiation errors
            await button_interaction.response.send_modal(
                next_modal_class(
                    user_email=current_modal.user_email,
                    user_id=user_id,
                    bot_instance=current_modal.bot_instance,
                    bot_config_obj=current_modal.bot_config
                )
            )
        except Exception as e_modal:
            print(f"Error instantiating/sending modal {next_modal_class.__name__} from button_callback: {e_modal}")
            # Attempt to send a message back to the user if the interaction is still available
            if not button_interaction.response.is_done():
                 await button_interaction.response.send_message("Failed to open the next step. Please try again.", ephemeral=True)
            else:
                 await button_interaction.followup.send("Failed to open the next step. Please try again.", ephemeral=True)

    button.callback = button_callback
    view.add_item(button)
    # This send_message is part of the successful path of _prepare_next_modal_step
    # If it fails, the exception will be caught by the on_submit method calling this helper.
    await interaction.response.send_message(confirmation_message, view=view, ephemeral=True)


# --- Discord UI Modals ---

class OrderFormStep1(discord.ui.Modal, title="Order Details - Step 1"):
    def __init__(self, user_email: str, bot_instance, bot_config_obj: BotConfig):
        super().__init__()
        self.user_email = user_email
        self.bot_instance = bot_instance
        self.bot_config = bot_config_obj

        self.form_fields = {}
        input_fields = {
            "order_number": ("Order Number", discord.TextStyle.short, True),
            "estimated_arrival_start_date": ("Arrival Start", discord.TextStyle.short, True),
            "estimated_arrival_end_date": ("Arrival End", discord.TextStyle.short, True),
            "product_image_url": ("Image URL", discord.TextStyle.short, True),
            "product_name": ("Product Name", discord.TextStyle.short, True),
        }
        for field_key, (label, style, required) in input_fields.items():
            self.form_fields[field_key] = create_text_input(label=label, style=style, required=required)
            self.add_item(self.form_fields[field_key])

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id
            self.bot_instance.temp_order_data[user_id] = {'email': self.user_email}

            await _prepare_next_modal_step(
                interaction=interaction,
                current_modal=self,
                user_id=user_id,
                data_key_name='step1_data',
                next_modal_class=OrderFormStep2,
                button_label="Continue to Step 2",
                confirmation_message="Step 1 completed! Click below to continue:"
            )
        except Exception as e:
            print(f"Error in OrderFormStep1.on_submit for user {interaction.user.id}: {e}")
            error_message = "An error occurred while processing Step 1. Please try again or contact support."
            if not interaction.response.is_done():
                await interaction.response.send_message(error_message, ephemeral=True)
            else:
                # This case might occur if _prepare_next_modal_step partially succeeded (sent a response) then failed.
                await interaction.followup.send(error_message, ephemeral=True)

class OrderFormStep2(discord.ui.Modal, title="Order Details - Step 2"):
    def __init__(self, user_email: str, user_id: int, bot_instance, bot_config_obj: BotConfig):
        super().__init__()
        self.user_email = user_email
        self.user_id = user_id
        self.bot_instance = bot_instance
        self.bot_config = bot_config_obj

        self.form_fields = {}
        input_fields = {
            "style_id": ("Style ID", discord.TextStyle.short, True),
            "product_size": ("Product Size", discord.TextStyle.short, True),
            "product_condition": ("Condition", discord.TextStyle.short, True),
            "purchase_price": ("Purchase Price", discord.TextStyle.short, True),
            "color": ("Color", discord.TextStyle.short, True),
        }
        for field_key, (label, style, required) in input_fields.items():
            self.form_fields[field_key] = create_text_input(label=label, style=style, required=required)
            self.add_item(self.form_fields[field_key])

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await _prepare_next_modal_step(
                interaction=interaction,
                current_modal=self,
                user_id=self.user_id,
                data_key_name='step2_data',
                next_modal_class=OrderFormStep3,
                button_label="Continue to Final Step",
                confirmation_message="Step 2 completed! Click below to continue:"
            )
        except Exception as e:
            print(f"Error in OrderFormStep2.on_submit for user {self.user_id}: {e}")
            error_message = "An error occurred while processing Step 2. Please try again or contact support."
            if not interaction.response.is_done():
                await interaction.response.send_message(error_message, ephemeral=True)
            else:
                await interaction.followup.send(error_message, ephemeral=True)

class OrderFormStep3(discord.ui.Modal, title="Order Details - Step 3"):
    def __init__(self, user_email: str, user_id: int, bot_instance, bot_config_obj: BotConfig):
        super().__init__()
        self.user_email = user_email
        self.user_id = user_id
        self.bot_instance = bot_instance
        self.bot_config = bot_config_obj

        user_specific_data = self.bot_instance.temp_order_data[self.user_id]
        self.step1_data = user_specific_data['step1_data']
        self.step2_data = user_specific_data.get('step2_data', {})

        self.form_fields = {}
        input_fields = {
            "shipping_address": ("Shipping Address", discord.TextStyle.paragraph, True),
            "notes": ("Additional Notes", discord.TextStyle.paragraph, False),
        }
        for field_key, (label, style, required) in input_fields.items():
            self.form_fields[field_key] = create_text_input(label=label, style=style, required=required)
            self.add_item(self.form_fields[field_key])

    async def on_submit(self, interaction: discord.Interaction):
        try:
            final_step_data = {key: field.value for key, field in self.form_fields.items()}
            merged_data = {**self.step1_data, **self.step2_data, **final_step_data}

            # Send initial confirmation to channel
            # This is the first interaction response. If it fails, the rest shouldn't proceed.
            await interaction.response.send_message(
                content=(
                    f"✅ **Order Submitted!**\n\n"
                    f"📦 **Product:** {merged_data['product_name']}\n"
                    f"💰 **Total Paid:** {merged_data['purchase_price']}\n"
                    f"🚚 **Estimated Arrival:** {merged_data['estimated_arrival_start_date']} to {merged_data['estimated_arrival_end_date']}\n"
                    f"📍 **Shipping To:** {merged_data['shipping_address']}"
                ),
                ephemeral=False,
            )
            print(f"Order submission message sent for user {self.user_id}.")

            # Attempt to send email
            try:
                await self.bot_config.email_service.send_single_email(
                    recipient_email=self.user_email,
                    email_data=merged_data,
                    email_template_data=self.bot_config.email_template
                )
                print(f"Confirmation email initiated for {self.user_email} by OrderFormStep3.")
            except Exception as e_email:
                print(f"Error sending email in OrderFormStep3 for user {self.user_id}: {e_email}")
                # Use followup as initial response has been sent
                await interaction.followup.send("Your order was submitted, but there was an issue sending the confirmation email. Please contact support if you don't receive it shortly.", ephemeral=True)

        except Exception as e_main:
            print(f"Error in OrderFormStep3.on_submit for user {self.user_id} (before email/cleanup): {e_main}")
            error_message = "An critical error occurred while finalizing your order. Please contact support."
            if not interaction.response.is_done(): # Should be done if initial message succeeded
                await interaction.response.send_message(error_message, ephemeral=True)
            else:
                # This followup is for errors *after* the initial "Order Submitted!" message
                # but *before* or outside the specific email error handling.
                await interaction.followup.send(error_message, ephemeral=True)
        finally:
            # Data cleanup should happen regardless of email success, but after main processing
            try:
                if self.user_id in self.bot_instance.temp_order_data:
                    del self.bot_instance.temp_order_data[self.user_id]
                    print(f"Successfully deleted temporary data for user {self.user_id}")
            except KeyError:
                # This might happen if data was already cleaned or never fully set
                print(f"No temporary data found for user {self.user_id} to delete during OrderFormStep3 cleanup (or already cleaned).")
            except AttributeError:
                print("Error: bot_instance does not have temp_order_data attribute or it's not a dict during OrderFormStep3 cleanup.")
            except Exception as e_cleanup:
                print(f"Unexpected error during temp_order_data cleanup for user {self.user_id}: {e_cleanup}")
