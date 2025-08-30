import json
import os

def load_config(filename="config.json"):
    """Loads configuration data from a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), '..', 'config', filename)
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {filepath}")
        return {}

def load_email_template(filename="email_template.json"):
    """Loads email template data from a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), '..', 'config', filename)
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Email template file not found at {filepath}")
        return {}
