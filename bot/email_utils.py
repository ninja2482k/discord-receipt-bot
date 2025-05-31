import re
import aiosmtplib
from aiosmtplib.errors import SMTPAuthenticationError, SMTPRecipientRefused, SMTPSenderRefused, SMTPDataError, SMTPServerDisconnected, SMTPHeloError, SMTPException, SMTPRecipientsRefused
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def is_valid_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.

    The regex pattern is structured as follows:
    - `^[a-zA-Z0-9_.+-]+`: Matches the local part of the email (before '@').
        - `^`: Asserts the start of the string.
        - `[a-zA-Z0-9_.+-]+`: Matches one or more occurrences of alphanumeric characters,
          dots, underscores, plus signs, or hyphens.
    - `@`: Matches the '@' symbol literally.
    - `[a-zA-Z0-9-]+`: Matches the domain name part (e.g., 'gmail', 'outlook').
        - `[a-zA-Z0-9-]+`: Matches one or more occurrences of alphanumeric characters or hyphens.
    - `\.`: Matches the dot separating the domain from the top-level domain (TLD).
        - `\.`: Escapes the dot to match it literally.
    - `[a-zA-Z0-9-.]+$`: Matches the TLD and any subdomains (e.g., 'com', 'co.uk').
        - `[a-zA-Z0-9-.]+`: Matches one or more occurrences of alphanumeric characters, hyphens, or dots.
        - `$`: Asserts the end of the string.

    Args:
        email (str): The email address string to validate.

    Returns:
        bool: True if the email address is valid according to the regex, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


async def send_email(recipient_email: str, email_data: dict, sender_email_address: str, sender_password_value: str, email_template_data: dict, smtp_config: dict):
    """
    Asynchronously sends an email with provided data using aiosmtplib.

    This function constructs an HTML email using a template, populates it with
    order-specific data, and sends it via an SMTP server. It handles various
    SMTP-related exceptions.

    Args:
        recipient_email (str): The email address of the recipient.
        email_data (dict): A dictionary containing data to populate the email template
                           (e.g., order number, product name).
        sender_email_address (str): The email address of the sender.
        sender_password_value (str): The password for the sender's email account.
        email_template_data (dict): A dictionary containing the email structure,
                                   typically with an "html_body" key.
        smtp_config (dict): A dictionary with SMTP server configuration,
                            including "smtp_server" and "smtp_port".

    Returns:
        None. Outputs status to console.
    """
    message = MIMEMultipart()
    message['From'] = sender_email_address
    message['To'] = recipient_email
    message['Subject'] = "Order Confirmation" # Consider making subject configurable

    # Populate the HTML body from the template
    html_body = email_template_data.get("html_body", "<p>Error: Email template not found.</p>")
    for key, value in email_data.items():
        html_body = html_body.replace(f"{{{{{key}}}}}", str(value)) # Ensure value is string

    message.attach(MIMEText(html_body, 'html'))

    try:
        # Get SMTP server details from smtp_config, with defaults
        smtp_server_address = smtp_config.get("smtp_server", "smtp.gmail.com")
        smtp_port_number = smtp_config.get("smtp_port", 587)

        # Establish connection with the SMTP server
        async with aiosmtplib.SMTP(hostname=smtp_server_address, port=smtp_port_number) as server:
            await server.login(sender_email_address, sender_password_value) # Authenticate
            # Send the email
            await server.sendmail(sender_email_address, recipient_email, message.as_string())
        print(f"Email sent to {recipient_email}")

    except SMTPAuthenticationError as e:
        # Authentication with the SMTP server failed (e.g., wrong username/password).
        print(f"SMTP Authentication Error for {recipient_email}: {e}")
    except SMTPRecipientsRefused as e:
        # All recipient addresses were refused by the server.
        print(f"All recipients refused for {recipient_email}: {e}")
    except SMTPRecipientRefused as e:
        # A specific recipient address was refused. The error object 'e' contains more details.
        # This might occur if the email address is invalid or the receiving server has issues.
        print(f"Recipient refused for {recipient_email}: {e.code} {e.message}")
    except SMTPSenderRefused as e:
        # The sender's email address was refused by the server.
        print(f"Sender refused for {recipient_email}: {e}")
    except SMTPDataError as e:
        # The SMTP server refused to accept the email data (e.g., message content issues).
        print(f"SMTP Data Error for {recipient_email}: {e}")
    except SMTPServerDisconnected as e:
        # The connection to the SMTP server was unexpectedly lost.
        print(f"SMTP Server disconnected for {recipient_email}: {e}")
    except SMTPHeloError as e:
        # The server refused the HELO/EHLO command (initial handshake error).
        print(f"SMTP Helo Error for {recipient_email}: {e}")
    except SMTPException as e:
        # A general exception from the aiosmtplib library not covered by more specific exceptions.
        print(f"SMTP General Error for {recipient_email}: {e}")
    except Exception as error:
        # Any other non-SMTP exception that might occur during the process.
        print(f"Generic error sending email to {recipient_email}: {error}")
