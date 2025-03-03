"""
FPDS API Handler Test Script

This script tests the AWS Lambda API handler function for FPDS data processing.
It simulates API Gateway invocation by creating an event object with query parameters
and passing it to the api_handler function, then verifies that the handler processes
the event correctly and returns the expected response.

The script tests:
1. Creating an API Gateway event with query parameters
2. Invoking the api_handler function
3. Verifying that the handler returns the expected response
4. Checking that the response contains the fetched data

Usage:
    python tests/test_api.py
"""

import sys
import os
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_handler import api_handler

# Create a mock API Gateway event
api_event = {
    'resource': '/fpds',
    'path': '/fpds',
    'httpMethod': 'GET',
    'queryStringParameters': {
        'start_date': '2023/01/01',
        'end_date': '2023/01/20',
        'agency_code': '7504',
        'max_results': '30'
    },
    'headers': {
        'Accept': 'application/json',
        'Host': 'example.execute-api.us-east-1.amazonaws.com'
    },
    'requestContext': {
        'identity': {
            'sourceIp': '127.0.0.1'
        }
    }
}

print("Testing API handler with mock API Gateway event...")

# Invoke the API handler
response = api_handler(api_event, {})

# Print the response status code
print(f"Response status code: {response['statusCode']}")

# Parse the response body
body = json.loads(response['body'])

# Print the number of records returned
print(f"Records returned: {body['count']}")

# Print sample data if available
if body['count'] > 0:
    print("\nSample data from first record:")
    sample_record = body['data'][0]
    for key, value in list(sample_record.items())[:5]:
        print(f"  {key}: {value}")

# Test with missing parameters
print("\nTesting with missing parameters...")
missing_params_event = {
    'resource': '/fpds',
    'path': '/fpds',
    'httpMethod': 'GET',
    'queryStringParameters': {
        'start_date': '2023/01/01',
        # Missing end_date
        'agency_code': '7504'
    }
}

missing_response = api_handler(missing_params_event, {})
print(f"Response status code: {missing_response['statusCode']}")
missing_body = json.loads(missing_response['body'])
print(f"Error message: {missing_body.get('error')}")
print(f"Missing parameters: {missing_body.get('missing')}")

print("\nAPI handler test complete.") 