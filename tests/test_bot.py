import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock
import discord
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import is_valid_email, load_config, load_email_template, validate_date_format, send_email

def test_email_validation():
    """Test the email validation function"""
    assert is_valid_email("test@example.com") == True
    assert is_valid_email("invalid-email") == False
    assert is_valid_email("test@domain") == False
    assert is_valid_email("test.name+label@example.com") == True
    assert is_valid_email("user.name@subdomain.example.com") == True
    assert is_valid_email("") == False
    assert is_valid_email("@example.com") == False

def test_config_loading(tmp_path):
    """Test the config loading function"""
    # Create a temporary config file
    config_file = tmp_path / "test_config.json"
    config_file.write_text('{"test_key": "test_value"}')
    
    config = load_config(str(config_file))
    assert config["test_key"] == "test_value"

def test_email_template_loading(tmp_path):
    """Test the email template loading function"""
    # Create a temporary template file
    template_file = tmp_path / "test_template.json"
    template_file.write_text('{"html_body": "Test {{variable}}"}')
    
    template = load_email_template(str(template_file))
    assert "html_body" in template
