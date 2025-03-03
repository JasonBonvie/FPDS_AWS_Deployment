#!/usr/bin/env python3
"""
FPDS API Example Usage

This script demonstrates how to use the FPDS API to retrieve contract data.
It includes examples of basic queries, filtering, and processing the results.
"""

import requests
import json
from datetime import datetime, timedelta
import argparse

# API endpoint
API_URL = "https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds"

def fetch_contracts(start_date, end_date, agency_code, max_results=10):
    """
    Fetch contracts from the FPDS API.
    
    Args:
        start_date: Start date for last modified date range (YYYY/MM/DD)
        end_date: End date for last modified date range (YYYY/MM/DD)
        agency_code: Agency code to filter by
        max_results: Maximum number of results to return
        
    Returns:
        dict: API response with count and data fields
    """
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "agency_code": agency_code,
        "max_results": max_results
    }
    
    print(f"Fetching contracts with parameters: {params}")
    
    response = requests.get(API_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def display_contract_summary(contract):
    """
    Display a summary of a contract.
    
    Args:
        contract: Contract data from the API
    """
    print(f"Title: {contract['title']}")
    print(f"Link: {contract['link']}")
    print(f"Modified: {contract['modified']}")
    
    # Display some key attributes if available
    attrs = contract.get('award_attributes', {})
    
    # Contract value
    if 'award.dollarValues.obligatedAmount' in attrs:
        print(f"Value: ${attrs['award.dollarValues.obligatedAmount']}")
    
    # Vendor name
    if 'award.vendor.vendorHeader.vendorName' in attrs:
        print(f"Vendor: {attrs['award.vendor.vendorHeader.vendorName']}")
    
    # Contract type
    if 'award.contractData.contractActionType' in attrs and 'award.contractData.contractActionType@description' in attrs:
        print(f"Type: {attrs['award.contractData.contractActionType@description']} ({attrs['award.contractData.contractActionType']})")
    
    print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description='Fetch and display FPDS contract data')
    
    # Default to last 30 days if no dates provided
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    
    parser.add_argument('--start-date', default=thirty_days_ago.strftime('%Y/%m/%d'),
                        help='Start date (YYYY/MM/DD)')
    parser.add_argument('--end-date', default=today.strftime('%Y/%m/%d'),
                        help='End date (YYYY/MM/DD)')
    parser.add_argument('--agency-code', default='7504',
                        help='Agency code')
    parser.add_argument('--max-results', type=int, default=5,
                        help='Maximum number of results to return')
    parser.add_argument('--output', help='Output file for JSON results')
    
    args = parser.parse_args()
    
    # Fetch contracts
    contracts = fetch_contracts(
        args.start_date,
        args.end_date,
        args.agency_code,
        args.max_results
    )
    
    if not contracts:
        print("No contracts found or error occurred.")
        return
    
    # Display results
    print(f"\nFound {contracts['count']} contracts\n")
    
    for contract in contracts['data']:
        display_contract_summary(contract)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(contracts, f, indent=2)
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main() 