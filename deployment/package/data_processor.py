"""
FPDS Data Processing Module

This module processes data retrieved from the FPDS ATOM feed. It applies field validation
and formatting based on the field configuration, and prepares the data for further use.

Key features:
- Processes FPDS data using field configuration
- Validates field values against regex patterns
- Formats field values according to configuration
- Handles both processed data from fetch_fpds_data and raw XML strings

Main functions:
- process_fpds_data: Processes data retrieved from fetch_fpds_data
- process_xml_string: Processes raw XML string data

The module works with the field configuration loaded from fields.json to ensure
that field values are properly validated and formatted according to the requirements.

Usage example:
    from atomreq import fetch_fpds_data
    from field_utils import load_fields_config
    
    data = fetch_fpds_data(last_mod_date, agency_code)
    fields_config = load_fields_config()
    processed_data = process_fpds_data(data, fields_config)
"""

from atomreq import clean_xml, flatten_xml
import xml.etree.ElementTree as ET
from field_utils import validate_field, format_field_value

def process_fpds_data(xml_data, fields_config):
    """
    Process FPDS data using field configuration.
    
    Args:
        xml_data: List of contract data from fetch_fpds_data
        fields_config: List of field configurations
        
    Returns:
        list: Processed and validated FPDS data
    """
    processed_entries = []
    
    for contract in xml_data:
        # Process each contract entry
        processed_contract = {}
        
        # Copy basic ATOM feed elements
        for key, value in contract.items():
            if key != "award_attributes" and not key.endswith("_attributes"):
                processed_contract[key] = value
        
        # Process award attributes if available
        if "award_attributes" in contract:
            award_attributes = contract["award_attributes"]
            
            # Filter and validate fields based on configuration
            for field_config in fields_config:
                field_name = field_config["name"]
                
                if field_name in award_attributes:
                    value = award_attributes[field_name]
                    
                    # Validate the field
                    if validate_field(field_name, value, fields_config):
                        # Format the field value
                        processed_contract[field_name] = format_field_value(field_name, value, fields_config)
                    else:
                        # Log invalid fields but still include them
                        print(f"Warning: Invalid value for {field_name}: {value}")
                        processed_contract[field_name] = value
        
        processed_entries.append(processed_contract)
    
    return processed_entries

def process_xml_string(xml_string, fields_config):
    """
    Process raw XML string using field configuration.
    
    Args:
        xml_string: Raw XML data from FPDS
        fields_config: List of field configurations
        
    Returns:
        list: Processed and validated FPDS data
    """
    # Clean the XML
    cleaned_xml = clean_xml(xml_string)
    
    # Parse the XML
    root = ET.fromstring(cleaned_xml)
    
    # Extract entries
    entries = []
    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        # Flatten the entry
        flat_entry = flatten_xml(entry)
        
        # Filter and validate fields
        processed_entry = {}
        for field_name in [f['name'] for f in fields_config]:
            if field_name in flat_entry:
                value = flat_entry[field_name]
                
                # Validate the field
                if validate_field(field_name, value, fields_config):
                    # Format the field value
                    processed_entry[field_name] = format_field_value(field_name, value, fields_config)
                else:
                    # Log invalid fields but still include them
                    print(f"Warning: Invalid value for {field_name}: {value}")
                    processed_entry[field_name] = value
        
        entries.append(processed_entry)
    
    return entries
