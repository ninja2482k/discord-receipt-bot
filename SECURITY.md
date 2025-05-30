# Security Policy

## Supported Versions

Currently, we are providing security updates for the following versions of Discord Receipt Bot:

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Discord Receipt Bot seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do not disclose the vulnerability publicly** until it has been addressed by the maintainers.
2. Email the details of the vulnerability to [your-email@example.com](mailto:your-email@example.com).
3. Include as much information as possible, such as:
   - A description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggestions for addressing the issue (if any)

## What to Expect

- We will acknowledge receipt of your vulnerability report within 48 hours.
- We will provide an estimated timeline for a fix and keep you updated on our progress.
- Once the vulnerability has been fixed, we will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous).

## Security Best Practices for Users

### Email Configuration
- Use app-specific passwords when configuring the email sender
- Consider using a dedicated email account for the bot
- Regularly rotate your email credentials

### Discord Bot Token
- Never share your bot token publicly
- Rotate your bot token if you suspect it has been compromised
- Use environment variables to store sensitive information rather than hardcoding them

### General Security
- Keep the bot code and dependencies updated
- Regularly review the permissions granted to the bot
- Monitor the bot's activity for any suspicious behavior

## Security Features

Discord Receipt Bot implements several security measures:

1. **Email Validation**: The bot validates email addresses before processing them
2. **Environment Variables**: Sensitive information is stored in environment variables
3. **Error Handling**: Comprehensive error handling to prevent information leakage
4. **Ephemeral Messages**: Sensitive user interactions use ephemeral messages where appropriate
5. **Data Cleanup**: User data is removed after processing to minimize data retention

## Version-Specific Security Information

### Version 3.0
- Added comprehensive SMTP error handling
- Improved email validation
- Enhanced data cleanup procedures
- Implemented additional permission checks

### Version 2.0
- Added environment variable support
- Improved error handling
- Implemented ephemeral messages for sensitive information

### Version 1.0
- Basic email validation
- Initial security features

Thank you for helping keep Discord Receipt Bot and its users safe!
