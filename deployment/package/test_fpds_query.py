#!/usr/bin/env python3
"""
Test script for FPDS API queries
"""

import requests
import json
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from atomreq import fetch_fpds_data, clean_xml, flatten_xml
from field_utils import load_fields_config
from data_processor import process_xml_string

def process_fpds_entry(entry):
    """Process a single FPDS entry"""
    result = {}
    
    # Get basic entry info using flatten_xml
    result.update(flatten_xml(entry))
    
    # Get content and process it
    content_elem = entry.find("{http://www.w3.org/2005/Atom}content")
    if content_elem is not None:
        # Extract and clean the XML content
        content_xml = content_elem.text
        
        # If content.text is empty, try to get XML from child elements
        if not content_xml or not content_xml.strip():
            if len(list(content_elem)) > 0:
                content_xml = "".join(ET.tostring(child, encoding='unicode') for child in content_elem)
        
        if content_xml and content_xml.strip():
            cleaned_xml = clean_xml(content_xml)
            try:
                content_root = ET.fromstring(cleaned_xml)
                award_data = flatten_xml(content_root)
                result["award_attributes"] = award_data
            except ET.ParseError as e:
                print(f"Error parsing content XML: {e}")
    
    return result

def test_fpds_query(params):
    """
    Test an FPDS query with the given parameters
    """
    all_processed_data = []
    start_index = 0
    
    while True:
        # Build the query string
        query = f"LAST_MOD_DATE:[{params['start_date']},{params['end_date']}]"
        
        if 'naics_code' in params:
            query += f"+PRINCIPAL_NAICS_CODE:{params['naics_code']}"
        
        if 'min_value' in params:
            query += f"+TOTAL_DOLLARS_OBLIGATED>={params['min_value']}"
        
        if 'max_value' in params:
            query += f"+TOTAL_DOLLARS_OBLIGATED<={params['max_value']}"
            
        if 'agency_code' in params:
            query += f"+AGENCY_CODE:{params['agency_code']}"
        
        # Construct FPDS ATOM feed URL with pagination
        url = (
            f"https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&VERSION=1.5"
            f"&q={query}"
            f"&start={start_index}&maxResults={params.get('max_results', 10)}"
        )
        
        print(f"\nTesting URL:\n{url}\n")
        
        # Make the request
        response = requests.get(url)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("\nSuccess! Processing response...")
            
            # Process the XML response
            root = ET.fromstring(response.text)
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")
            
            if not entries:
                break  # No more entries found
                
            for entry in entries:
                processed_entry = process_fpds_entry(entry)
                if processed_entry:
                    all_processed_data.append(processed_entry)
            
            print(f"Processed {len(entries)} entries in this batch")
            start_index += len(entries)
        else:
            print("\nError response:")
            print(response.text)
            break
    
    # Save all processed results
    output_file = "test_processed.json"
    with open(output_file, "w") as f:
        json.dump(all_processed_data, f, indent=2)
        
    print(f"\nTotal processed entries: {len(all_processed_data)}")
    print(f"Results saved to {output_file}")
    
    # Print sample of first result
    if all_processed_data:
        print("\nSample of first result:")
        first_entry = all_processed_data[0]
        print(json.dumps(first_entry, indent=2))

def main():
    # Test parameters
    params = {
        'start_date': '2025/01/01',
        'end_date': '2025/01/02',
        'naics_code': '541512',  # Computer Systems Design Services
        'min_value': '50000',
        'max_value': '500000',
        'max_results': 100
    }
    
    print("Testing with filters...")
    test_fpds_query(params)
    
    print("\n\nTesting with basic parameters only...")
    basic_params = {
        'start_date': '2025/01/01',
        'end_date': '2025/01/02',
        'max_results': 100
    }
    test_fpds_query(basic_params)

if __name__ == "__main__":
    main() 