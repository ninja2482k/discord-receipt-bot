# Discord Order & Diagnostic Bot

A simple and extendable Discord bot that handles **order forms**, runs **diagnostic checks**, and **sends confirmation emails to users**. With fun features and utility tools on the way, this bot is perfect for community servers and service-based Discords.

This bot is designed for Discord servers that need a basic but reliable tool to:

- Collect orders using command-based forms (e.g., `/order`)
- Run simple diagnostics or bot status checks (e.g., `/diagnostics`, `/ping`)
- Automatically send order confirmation emails to users (configurable)

Perfect for growing communities, service-based servers (e.g., digital services, commissions), or development showcases.

---

## 💡 Features

- 📦 `/order_form` — Starts a multi-step order form via slash command and sends a confirmation email upon completion.
- 🩺 `/run_diagnostics` — Performs bot diagnostics including uptime, server count, user count, and latency.
- 핑 `/ping` — Responds with Pong! and the bot's current latency.
- ✉️ Auto-email confirmations using Gmail SMTP (configurable for other providers).

> 📸 **Reminder**: Add screenshots or a short video of you using these commands in your README or repo — it helps others understand what the bot does in action!

---

## 🧱 Project Structure

The bot's codebase is organized into several modules for better maintainability and clarity:

-   **`main.py`**: The main entry point for the Discord bot. Initializes the bot, loads configurations, sets up commands (via `bot_commands.py`), and connects to Discord.
-   **`config_loader.py`**: Handles loading of configurations from `config.json` (for general settings like SMTP) and `email_template.json` (for email content).
-   **`email_utils.py`**: Contains functions for sending emails (including order confirmations using `aiosmtplib`) and validating email addresses.
-   **`discord_ui.py`**: Defines the multi-step Discord modals (`OrderFormStep1`, `OrderFormStep2`, `OrderFormStep3`) and UI helper functions used in the order submission process.
-   **`bot_commands.py`**: Contains the definitions and logic for all slash commands available to the bot (e.g., `/ping`, `/order_form`, `/run_diagnostics`).
-   **`.env.example`**: An example file showing the required environment variables. You should copy this to `.env` and fill in your credentials.
-   **`requirements.txt`**: Lists all Python package dependencies.
-   **`config.json`**: Configuration file for non-sensitive settings, like SMTP server and port.
-   **`email_template.json`**: JSON file defining the HTML body and other parts of the confirmation email.

---

## 🛠 Installation

To run the bot locally or on your server:

### 1. Clone or Download the Repo

#### Option A: Clone with Git
```bash
git clone https://github.com/yourusername/your-repo-name.git # Replace with your repo URL
cd your-repo-name
```

#### Option B: Manual Download
- Click the green **Code** button on the GitHub repository page.
- Select **Download ZIP**.
- Extract the downloaded folder.

---

### 2. Requirements

Make sure you have **Python 3.9+** and `pip` installed.

#### Install Python & pip:

- Visit [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Download and install the latest Python 3 version (make sure to check “Add Python to PATH” during setup on Windows).
- After installation, verify by opening a terminal or command prompt and typing:
```bash
python --version
pip --version
```

---

### 3. Install Dependencies

Navigate to the project's root directory in your terminal and install the required packages using:

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration Guide

Setting up the bot involves configuring your Discord Bot Token, email credentials, and potentially SMTP settings.

### Step 1: Create a Discord Bot Application

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Click **“New Application”**, give it a name, and agree to the terms.
3.  Navigate to the **Bot** tab on the left sidebar.
4.  Click **“Add Bot”** and confirm.
5.  Under **Privileged Gateway Intents**, enable:
    *   **Presence Intent** (Optional, but good for some diagnostic features or future enhancements)
    *   **Message Content Intent** (Required if you plan to use prefix commands or read message content; less critical for slash-command-only bots but good to enable for flexibility).
6.  Go to **OAuth2 > URL Generator** (under OAuth2 section):
    *   In "Scopes", select `bot` and `applications.commands`.
    *   In "Bot Permissions" below, select necessary permissions. For ease of setup, you can select `Administrator`, but for production, grant only the permissions your bot truly needs (e.g., Send Messages, Read Message History, Embed Links).
    *   Copy the generated URL and paste it into your browser to invite the bot to your Discord server.

### Step 2: Get the Bot Token

-   In the **Bot** tab of your application on the Discord Developer Portal, click **“Reset Token”** (or "View Token" if available).
-   Copy the token. This is your `DISCORD_BOT_TOKEN`. **Treat this like a password and never share it publicly.**

### Step 3: Set Up Gmail App Password (If Using Gmail for Sending Emails)

If you intend to use a Gmail account to send confirmation emails, you'll need an "App Password" if Two-Factor Authentication (2FA) is enabled on that Google account.

1.  Go to your Google [Account Settings > Security](https://myaccount.google.com/security).
2.  Ensure **2-Step Verification** is enabled.
3.  Go to [App Passwords](https://myaccount.google.com/apppasswords) (you might need to sign in again).
4.  Under "Select app", choose **Mail**.
5.  Under "Select device", choose **Other (Custom name)**.
6.  Name it (e.g., "Discord Bot Orders") and click **Generate**.
7.  Copy the 16-character generated App Password. This will be your `SENDER_PASSWORD`.

### Step 4: Configure Environment Variables and JSON Files

This bot uses a `.env` file for sensitive credentials and JSON files (`config.json`, `email_template.json`) for other settings.

**A. Environment Variables (`.env` file):**

1.  In the root directory of the project, find the file named `.env.example`.
2.  Create a copy of `.env.example` and rename the copy to `.env`.
3.  Open the `.env` file with a text editor.
4.  Fill in your actual credentials:
    *   `SENDER_EMAIL`: The email address the bot will use to send emails (e.g., your Gmail address).
    *   `SENDER_PASSWORD`: The password for the sender's email account (e.g., the Gmail App Password you generated).
    *   `DISCORD_BOT_TOKEN`: The Discord bot token you copied in Step 2.

    Example `.env` content:
    ```env
    # .env (example, replace with your actual values)
    SENDER_EMAIL=your_email@gmail.com
    SENDER_PASSWORD=youractualapppassword
    DISCORD_BOT_TOKEN=youractualdiscordbottoken
    ```
    **Important:** Add `.env` to your `.gitignore` file if it's not already there. This prevents you from accidentally committing your sensitive credentials to version control.

**B. Non-Sensitive Settings (`config.json`):**

The `config.json` file is used for non-sensitive configurations, primarily the SMTP server and port for sending emails. Default values are provided for Gmail.

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```
If you are using a different email provider, update `smtp_server` and `smtp_port` in `config.json` accordingly. The optional SMTP variables mentioned in `.env.example` (`SMTP_SERVER`, `SMTP_PORT`) are for user reference if they choose to customize the email sending logic to prioritize environment variables for these settings (current code does not do this by default).

**C. Email Template (`email_template.json`):**

The `email_template.json` file defines the content of the order confirmation email. You can customize the `html_body` (which supports placeholders like `{{product_name}}`) and other email fields here.

---

## ▶️ Run the Bot

Once all configurations are set up:

1.  Open your terminal or command prompt.
2.  Navigate to the root directory of the project.
3.  Run the bot using Python:

```bash
python main.py
```

If everything is configured correctly, you should see messages in your console indicating the bot has logged in and is ready. Ensure your bot is invited to a server and has the necessary permissions.

---

## 💬 Commands

| Command             | Description                                               |
|---------------------|-----------------------------------------------------------|
| `/order_form`       | Starts a multi-step order submission process via modals.  |
| `/run_diagnostics`  | Checks bot status, uptime, server/user count, and latency. |
| `/ping`             | Responds with Pong! and the bot's current latency.        |

More commands (fun tools, integrations, and automation) are planned for future development.

---

## ✨ Recent Improvements & Refactoring

This bot has undergone significant enhancements to improve security, reliability, and maintainability:

-   **Modular Codebase**: The project has been refactored into multiple Python modules (`main.py`, `config_loader.py`, `email_utils.py`, `discord_ui.py`, `bot_commands.py`) for better organization and separation of concerns.
-   **Secure Credential Management**: Sensitive credentials (Bot Token, Sender Email, Sender Password) are managed securely using environment variables via a `.env` file, loaded by `python-dotenv`. An `.env.example` file is provided as a template.
-   **Asynchronous Operations**: Email sending now uses `aiosmtplib` for asynchronous SMTP communication, improving bot responsiveness by not blocking other operations.
-   **Standardized Slash Commands**: All primary bot commands have been implemented as Discord slash commands for a modern user experience.
-   **Improved UI for Orders**: The order submission process uses a sequence of Discord Modals for a better user interface.
-   **Concurrency Support**: Order form data handling is designed to manage data for multiple users concurrently using a dictionary within the bot instance.
-   **Detailed Error Handling**: Email sending includes specific exception handling for `aiosmtplib` errors. Bot startup includes checks for critical configurations like `BOT_TOKEN`.
-   **Configurable Settings**: SMTP server/port are configurable via `config.json`. The email content is templated in `email_template.json`.

---

## 🧱 Technologies Used

-   **Python** — Core programming language
-   **discord.py** — Main Discord bot framework for Python
-   **python-dotenv** — For loading environment variables from `.env` files
-   **aiosmtplib** — For asynchronous SMTP communication (sending emails)
-   **Standard Library Modules**: `os`, `time`, `json`, `typing`, `re` (used across different modules)

---

## 🤝 Contributing

We’d love your help! Even if you’re new to GitHub, contributing is easy:

### 📦 How to Contribute

1.  **Fork** this repo (top right corner of the GitHub page)
2.  **Clone** your fork:
    ```bash
    git clone https://github.com/yourusername/your-fork-name.git # Replace with your fork's URL
    cd your-fork-name
    ```
3.  **Create a branch** for your changes:
    ```bash
    git checkout -b feature/your-new-feature-name
    ```
4.  **Make your changes**, then commit them:
    ```bash
    git add .
    git commit -m "feat: implemented a cool new feature" # Use a descriptive commit message
    ```
5.  **Push** your changes to your fork:
    ```bash
    git push origin feature/your-new-feature-name
    ```
6.  **Open a Pull Request** on the original repository's GitHub page. 🎉

### ✅ Contribution Rules

-   Keep your code clean, readable, and well-commented where necessary.
-   Follow the existing code structure and style.
-   Ensure each pull request focuses on a single feature or bug fix.
-   Use meaningful and descriptive commit messages.

Even small improvements or documentation updates are welcome!

---

## 📜 License

This project is licensed under the [MIT License](LICENSE). (Ensure you have a LICENSE file if you mention it).

---

## 📫 Contact

Created by [calvin fernandes](https://github.com/ninja2482k)
Feel free to reach out via GitHub issues or discussions on the repository!
