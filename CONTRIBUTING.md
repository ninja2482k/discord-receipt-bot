# Contributing to Discord Receipt Bot

Thank you for your interest in contributing to the Discord Receipt Bot! This document provides guidelines and instructions for contributing to this project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Setting Up the Development Environment](#setting-up-the-development-environment)
  - [Running the Bot Locally](#running-the-bot-locally)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Style Guidelines](#style-guidelines)
  - [Code Style](#code-style)
  - [Commit Messages](#commit-messages)
- [Project Structure](#project-structure)

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

### Setting Up the Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/discord-receipt-bot.git
   cd discord-receipt-bot
   ```
3. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Bot Locally

1. Create a `.env` file in the project root with the following variables:
   ```
   SENDER_EMAIL=your_email@example.com
   SENDER_PASSWORD=your_email_password
   DISCORD_BOT_TOKEN=your_discord_bot_token
   ```

2. Run the bot:
   ```bash
   python main.py
   ```

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Any additional context that might be helpful

### Suggesting Enhancements

We welcome suggestions for enhancements! Please create an issue with:
- A clear, descriptive title
- A detailed description of the proposed enhancement
- Any relevant examples or mockups
- Explanation of why this enhancement would be useful

### Pull Requests

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or
   ```bash
   git checkout -b fix/issue-you-are-fixing
   ```

2. Make your changes and commit them with clear, descriptive commit messages

3. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a pull request against the main repository's `main` branch

5. In your pull request description, explain the changes you've made and reference any related issues

## Style Guidelines

### Code Style

- Follow PEP 8 guidelines for Python code
- Use 4 spaces for indentation (not tabs)
- Keep line length to a maximum of 100 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## Project Structure

- `main.py`: The main bot application
- `config.json`: Configuration settings for the bot
- `email_template.json`: Template for email messages
- `.env`: Environment variables (not committed to repository)

Thank you for contributing to the Discord Receipt Bot!
