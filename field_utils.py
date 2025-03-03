"""
FPDS Field Utilities Module

This module provides utilities for working with FPDS field configurations defined in fields.json.
It handles loading field definitions, validating field values against regex patterns, and
formatting field values according to configuration requirements.

Key features:
- Loads field configuration from fields.json
- Validates field values against regex patterns defined in the configuration
- Formats field values according to configuration (e.g., adding quotes)

Main functions:
- load_fields_config: Loads field configuration from fields.json
- validate_field: Validates a field value against its regex pattern
- format_field_value: Formats a field value according to its configuration

The fields.json file contains definitions for FPDS fields, including:
- Field name
- Field description
- Whether the field should be quoted
- Regex pattern for validation

Usage example:
    fields_config = load_fields_config()
    is_valid = validate_field('AGENCY_CODE', '7504', fields_config)
    formatted_value = format_field_value('AGENCY_CODE', '7504', fields_config)
"""

import os
import json
import re

def load_fields_config(config_path=None):
    """
    Load field configuration from fields.json.
    
    Args:
        config_path: Optional path to fields.json file
                    If None, will look in the current directory
                    
    Returns:
        list: List of field configurations
    """
    # Default to fields.json in the current directory
    if not config_path:
        config_path = os.path.join(os.path.dirname(__file__), 'fields.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading fields configuration: {str(e)}")
        # Return an empty list as fallback
        return []

def validate_field(field_name, value, fields_config):
    """
    Validate a field value against its regex pattern.
    
    Args:
        field_name: Name of the field to validate
        value: Value to validate
        fields_config: List of field configurations
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Find the field configuration
    field_config = next((f for f in fields_config if f['name'] == field_name), None)
    
    # If no configuration or no regex, consider it valid
    if not field_config or 'regex' not in field_config:
        return True
        
    # Convert value to string for regex matching
    value_str = str(value)
    
    # Validate against the regex pattern
    try:
        return re.match(field_config['regex'], value_str) is not None
    except Exception as e:
        print(f"Error validating {field_name}: {str(e)}")
        return False

def format_field_value(field_name, value, fields_config):
    """
    Format a field value according to its configuration.
    
    Args:
        field_name: Name of the field to format
        value: Value to format
        fields_config: List of field configurations
        
    Returns:
        The formatted value
    """
    # Find the field configuration
    field_config = next((f for f in fields_config if f['name'] == field_name), None)
    
    # If no configuration, return as is
    if not field_config:
        return value
        
    # Apply quotes if required
    if field_config.get('quotes', False) and isinstance(value, str):
        return f'"{value}"'
    
    return value
