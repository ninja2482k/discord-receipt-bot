import json

def load_config(filename="config.json"):
    """Loads configuration data from a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)

def load_email_template(filename="email_template.json"):
    """Loads email template data from a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)
