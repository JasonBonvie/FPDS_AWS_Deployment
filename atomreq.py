#!/usr/bin/env python
"""
FPDS Data Retrieval Module

This module provides functionality to fetch contract data from the Federal Procurement 
Data System (FPDS) ATOM feed. It handles the retrieval, parsing, and initial processing 
of contract data.

Key features:
- Fetches contract data from FPDS ATOM feed using specified parameters
- Supports pagination to retrieve more than the 10-record limit per request
- Cleans and parses XML data from the FPDS response
- Flattens hierarchical XML structure into a dictionary format
- Saves processed JSON data to files (optional)

Main function:
- fetch_fpds_data: Retrieves contract data based on date range and agency code

Helper functions:
- clean_xml: Sanitizes XML strings to handle common issues
- flatten_xml: Converts hierarchical XML elements into a flat dictionary

Usage example:
    last_mod_date = ("2022/01/01", "2022/05/01")
    agency_code = "7504"
    data = fetch_fpds_data(last_mod_date, agency_code, max_results=20)
"""

import requests
import xml.etree.ElementTree as ET
import json
import html
import re
import os
import time

def clean_xml(xml_string):
    """
    Clean up the XML string by replacing unescaped ampersands with '&amp;'.
    You can expand this function to handle other common issues.
    """
    # Replace & that are not already part of a valid entity.
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', xml_string)
    return cleaned

def flatten_xml(elem, parent_key="", sep="."):
    """
    Recursively flattens an XML element into a dictionary.
    For each element, the key is built as a combination of parent tags and the current tag.
    Attributes are appended with an '@' sign.
    """
    items = {}
    tag = elem.tag.split('}')[-1]
    new_key = f"{parent_key}{sep}{tag}" if parent_key else tag

    # If element has text and no children, record it.
    if elem.text and elem.text.strip() and not list(elem):
        items[new_key] = elem.text.strip()
    
    # Record attributes of the element.
    for attr, val in elem.attrib.items():
        items[f"{new_key}@{attr}"] = val

    # Recursively process child elements.
    for child in elem:
        items.update(flatten_xml(child, new_key, sep=sep))
    
    return items

def fetch_fpds_data(last_mod_date, agency_code, max_results=10,
                    output_json=None, additional_params=None):
    """
    Fetch data from FPDS ATOM feed with pagination support.
    
    Args:
        last_mod_date: Tuple of (start_date, end_date) for last modified date range
        agency_code: Agency code to filter by
        max_results: Maximum number of results to return (note: API returns max 10 per request)
        output_json: Optional path to save JSON output (for local testing)
        additional_params: Optional dict containing additional search parameters:
            - award_type: Type of award (BPA Call, Purchase Order, etc.)
            - contract_type: Type of contract (IDV or Award)
            - value_range: Tuple of (min_value, max_value) for contract value range
            - naics_code: NAICS code to filter by
            - title_keyword: Keyword to search in contract titles
        
    Returns:
        list: Processed FPDS data
    """
    all_contracts = []
    page_size = 10  # FPDS ATOM feed is limited to 10 records per request
    num_pages = (max_results + page_size - 1) // page_size  # Ceiling division
    
    print(f"Fetching up to {max_results} records ({num_pages} pages of {page_size} records each)")
    
    # Build the base query string
    query = f"LAST_MOD_DATE:[{last_mod_date[0]},{last_mod_date[1]}]+AGENCY_CODE:{agency_code}"
    
    # Add additional search parameters if provided
    if additional_params:
        if 'award_type' in additional_params:
            query += f"+AWARD_TYPE:\"{additional_params['award_type']}\""
        
        if 'contract_type' in additional_params:
            query += f"+CONTRACT_TYPE:\"{additional_params['contract_type']}\""
        
        if 'value_range' in additional_params:
            min_val, max_val = additional_params['value_range']
            query += f"+BASE_AND_ALL_OPTIONS_VALUE:[{min_val},{max_val}]"
        
        if 'naics_code' in additional_params:
            query += f"+NAICS_CODE:{additional_params['naics_code']}"
        
        if 'title_keyword' in additional_params:
            # Add title keyword search
            query += f"+TITLE:\"{additional_params['title_keyword']}\""
    
    for page in range(num_pages):
        start_index = page * page_size
        
        # Construct FPDS ATOM feed URL with pagination
        fpds_url = (
            f"https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&VERSION=1.5"
            f"&q={query}"
            f"&start={start_index}&maxResults={page_size}"
        )
        
        print(f"Fetching page {page+1}/{num_pages} (records {start_index+1}-{start_index+page_size})")
        
        response = requests.get(fpds_url)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            continue
        
        # Parse the XML response
        try:
            root = ET.fromstring(response.content)
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")
            
            if not entries:
                print(f"No more entries found on page {page+1}")
                break
                
            print(f"Found {len(entries)} entries on page {page+1}")
            
            # Process each entry
            for entry in entries:
                # Extract basic ATOM feed elements
                contract = {}
                
                # Get title
                title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                if title_elem is not None and title_elem.text:
                    contract["title"] = title_elem.text
                
                # Get link
                link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
                if link_elem is not None and "href" in link_elem.attrib:
                    contract["link"] = link_elem.attrib["href"]
                
                # Get modified date
                modified_elem = entry.find("{http://www.w3.org/2005/Atom}modified")
                if modified_elem is not None and modified_elem.text:
                    contract["modified"] = modified_elem.text
                
                # Get content
                content_elem = entry.find("{http://www.w3.org/2005/Atom}content")
                if content_elem is not None:
                    # Extract and clean the XML content
                    content_xml = content_elem.text
                    
                    # If content.text is empty, try to get XML from child elements
                    if not content_xml or not content_xml.strip():
                        # Check if there are child elements in the content
                        if len(list(content_elem)) > 0:
                            # Concatenate XML from all child elements
                            content_xml = "".join(ET.tostring(child, encoding='unicode') for child in content_elem)
                            # Unescape HTML entities
                            content_xml = html.unescape(content_xml)
                    
                    if content_xml and content_xml.strip():
                        # Remove debug print
                        # print(f"DEBUG - Content XML (first 100 chars): {content_xml[:100]}")
                        
                        cleaned_xml = clean_xml(content_xml)
                        
                        try:
                            # Parse the content XML
                            content_root = ET.fromstring(cleaned_xml)
                            
                            # Flatten the XML structure
                            award_data = flatten_xml(content_root)
                            
                            # Save all XML details under one key
                            contract["award_attributes"] = award_data
                        except ET.ParseError as e:
                            print(f"Error parsing content XML: {e}")
                            # Remove debug print
                            # print(f"DEBUG - Cleaned XML (first 100 chars): {cleaned_xml[:100]}")
                
                all_contracts.append(contract)
                
                # Break if we've reached the maximum number of results
                if len(all_contracts) >= max_results:
                    break
            
            # Break if we've reached the maximum number of results
            if len(all_contracts) >= max_results:
                break
                
        except ET.ParseError as e:
            print(f"Error parsing XML response: {e}")
    
    # Save the structured JSON output if output_json is provided
    if output_json and all_contracts:
        with open(output_json, "w", encoding="utf-8") as json_file:
            json.dump(all_contracts, json_file, indent=4)
        print(f"Structured JSON data saved to {output_json}")
    
    print(f"Total records fetched: {len(all_contracts)}")
    return all_contracts

# Example usage - only run this if the script is executed directly
if __name__ == "__main__":
    last_mod_date = ("2022/01/01", "2022/05/01")  # Date range
    agency_code = "7504"  # Specific agency
    fetch_fpds_data(
        last_mod_date, 
        agency_code,
        max_results=20,  # Fetch 20 records (2 pages)
        output_json="/Users/jasonbonvie/Desktop/fpds_data.json"
    )