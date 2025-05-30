# Discord Order & Diagnostic Bot

A simple and extendable Discord bot that handles **order forms**, runs **diagnostic checks**, and even **sends confirmation emails to users just like StockX**! With fun features and utility tools on the way, this bot is perfect for community servers and service-based Discords.

This bot is designed for Discord servers that need a basic but reliable tool to:

- Collect orders using command-based forms (e.g., `/order`)
- Run simple diagnostics or bot status checks (e.g., `/diagnostics`)
- Automatically send order confirmation emails to users (configurable)
- Eventually include fun community features and helpful utilities!

Perfect for growing communities, service-based servers (e.g., digital services, commissions), or development showcases.

---

## 💡 Features

- 📦 `/order` — Starts an order form via command and sends confirmation to email
- 🩺 `/diagnostics` — Performs bot diagnostics and system checks
- ✉️ Auto-email confirmations using Gmail SMTP
- 🎉 More commands coming soon (fun & utility tools like timers, reminders, polls)

> 📸 **Reminder**: Add screenshots or a short video of you using these commands in your README or repo — it helps others understand what the bot does in action!

---

## 🛠 Installation

To run the bot locally or on your server:

### 1. Clone or Download the Repo

#### Option A: Clone with Git
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

#### Option B: Manual Download
- Click the green **Code** button
- Select **Download ZIP**
- Extract the folder

---

### 2. Requirements

Make sure you have **Python 3.9+** and `pip` installed.

#### Install Python & pip:

- Visit [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Download and install the latest Python 3 version (make sure to check “Add Python to PATH” during setup)
- After install, check versions:
```bash
python --version
pip --version
```

---

### 3. Install Dependencies

Install the required packages using:

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration Guide

### Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **“New Application”** → Name it → Go to **Bot** tab → Click **“Add Bot”**
3. Turn ON:
   - **Presence Intent**
   - **Message Content Intent**
4. Go to **OAuth2 > URL Generator**
   - Scopes: `bot`
   - Bot Permissions: `Administrator`
   - Copy the generated link and invite the bot to your Discord server

### Step 2: Get the Bot Token

- In the Bot tab, click “Reset Token” → Copy it (you’ll use this in config)

### Step 3: Set Up Gmail App Password

To send confirmation emails, you need a Gmail "App Password":

1. Go to your Google [Account Settings > Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select **Mail**, device: "Other" → Name it anything → Copy password

### Step 4: Configure Bot Settings

This bot uses a combination of a `.env` file for sensitive credentials and `config.json` for other, non-sensitive settings.

**Sensitive Credentials (`.env` file):**

Create a `.env` file in the root directory of the project. This file will store your Discord Bot Token, Sender Email, and Email Password. The application uses the `python-dotenv` library to load these variables automatically.

Add the following lines to your `.env` file, replacing the placeholder values with your actual credentials:

```env
# .env (example)
DISCORD_BOT_TOKEN=your_actual_bot_token
SENDER_EMAIL=your_sender_email@example.com
SENDER_PASSWORD=your_email_password
```

**Important:** Add `.env` to your `.gitignore` file to prevent committing your secrets to version control. If you don't have a `.gitignore` file, create one in the root directory and add `.env` to it.

**Non-Sensitive Settings (`config.json`):**

The `config.json` file is used for non-sensitive configurations, such as the SMTP server and port. Default values are provided for Gmail.

```json
{
  "email": "",
  "email_password": "",
  "bot_token": "",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```
The `email`, `email_password`, and `bot_token` fields in `config.json` are placeholders and are overridden by the values in your `.env` file.

Save both files after making your changes.

---

## ▶️ Run the Bot

Run your bot with:

```bash
python main.py
```

Make sure your bot is in the server and has correct permissions.

---

## 💬 Commands

| Command        | Description                            |
|----------------|----------------------------------------|
| `/order`       | Starts a simple order form process and sends confirmation |
| `/diagnostics` | Checks if the bot is active and functioning properly |
| `/ping`        | Responds with Pong! and the bot's latency.         |

More commands (fun tools, integrations, and automation) are in development.

---

## ✨ Recent Improvements

This bot has undergone several enhancements to improve security, reliability, and maintainability:

- **Enhanced Security**: Sensitive credentials (Bot Token, Sender Email, Sender Password) have been moved from `config.json` to environment variables managed via a `.env` file.
- **Improved Concurrency**: Order form data handling has been refactored to support multiple concurrent users without data conflicts.
- **Detailed Error Logging**: Email sending functionality now includes more specific error catching and logging for `aiosmtplib` exceptions, aiding in troubleshooting.
- **Code Refactoring**:
    - UI `TextInput` components are now created using a dedicated helper function, making the modal definitions cleaner.
    - Email sending has been transitioned to `aiosmtplib`, enabling asynchronous operations and improving bot responsiveness.
- **Standardized Commands**: Bot commands are being standardized to use Discord's slash command interface (e.g., `/ping` now includes latency).
- **Configurable SMTP**: SMTP server and port are now configurable via `config.json`, providing flexibility for different email providers.

---

## 🧱 Technologies Used

- **Python** — Programming language
- **discord.py** — Discord bot framework for Python
- **dotenv** — Load secrets from `.env` files
- **asyncio** — For handling async tasks and commands
- **aiosmtplib** — For asynchronous SMTP communication (sending emails)
- **email.message** — For formatting the emails sent to users

---

## 🤝 Contributing

We’d love your help! Even if you’re new to GitHub, contributing is easy:

### 📦 How to Contribute

1. **Fork** this repo (top right corner of the GitHub page)
2. **Clone** your fork:
   ```bash
   git clone https://github.com/yourusername/your-fork-name.git
   cd your-fork-name
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**, then:
   ```bash
   git commit -m "feat: added a cool feature"
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** on GitHub 🎉

### ✅ Contribution Rules

- Keep your code clean and readable
- Follow the existing code structure
- Keep each pull request focused on one feature/fix
- Use meaningful commit messages

Even small improvements are welcome!

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 📫 Contact

Created by [calvin fernandes](https://github.com/ninja2482k)  
Feel free to reach out via GitHub issues or discussions!
