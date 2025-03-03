"""
Test script for FPDS data processing functionality.

This script tests the data processing functionality by:
1. Fetching data from the FPDS ATOM feed
2. Loading field configuration
3. Processing the data using the field configuration
4. Validating the processed data

The script demonstrates the complete data processing pipeline from
fetching raw data to producing validated and formatted output.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
from atomreq import fetch_fpds_data
from field_utils import load_fields_config
from data_processor import process_fpds_data

print("Testing FPDS data processing...")

# Load field configuration
fields_config = load_fields_config()
print(f"Loaded {len(fields_config)} field configurations")

# Set up test parameters
last_mod_date = ("2022/01/01", "2022/05/01")
agency_code = "7504"
max_results = 500  # Fetch 30 records (will require 3 pages)

print(f"Fetching data for agency {agency_code} with date range {last_mod_date}")

# Get raw data with pagination
data = fetch_fpds_data(
    last_mod_date, 
    agency_code, 
    max_results,
    output_json="test_raw.json"
)

print(f"Fetched {len(data)} entries")

# Verify results
print(f"Retrieved {len(data)} entries")
if data:
    print("\nSample data in first entry:")
    sample_entry = data[0]
    for key in ["title", "link", "modified"]:
        if key in sample_entry:
            print(f"  {key}: {sample_entry[key]}")
    
    # Process the data
    print("\nProcessing data with field configuration...")
    processed_data = process_fpds_data(data, fields_config)
    
    print(f"Processed {len(processed_data)} entries")
    
    # Save processed data
    with open("test_processed.json", "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2)
    
    print("Processed data saved to test_processed.json")
    
    print("\nTest completed successfully!")
else:
    print("No data retrieved. Test failed.")
