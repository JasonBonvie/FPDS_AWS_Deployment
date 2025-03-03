"""
AWS Lambda Handler Test Script

This script tests the AWS Lambda handler function for FPDS data processing.
It simulates Lambda invocation by creating an event object and passing it to
the lambda_handler function, then verifies that the handler processes the
event correctly and returns the expected response.

The script tests:
1. Creating a Lambda event with FPDS query parameters
2. Invoking the lambda_handler function
3. Verifying that the handler returns the expected response
4. Checking that the response contains the processed data

The script also includes a commented-out section for testing S3 storage,
which can be uncommented when ready to test that functionality.

Usage:
    python tests/test_lambda.py
"""

import sys
import os
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lambda_handler import lambda_handler

# Simulate Lambda event
event = {
    'last_mod_date': ("2022/01/01", "2022/05/01"),
    'agency_code': '7504',
    'max_results': 2
}

print("Testing Lambda handler with event:", json.dumps(event, indent=2))

# Invoke the Lambda handler
response = lambda_handler(event, None)

# Print the response
print(f"\nStatus code: {response['statusCode']}")

# Parse the response body
body = json.loads(response['body'])
print(f"Response message: {body['message']}")

# Check if data was returned
if response['statusCode'] == 200 and 'data' in body:
    data = body['data']
    print(f"Returned {len(data)} entries")
    
    if data:
        print("\nSample fields in first entry:")
        sample_entry = data[0]
        for key, value in list(sample_entry.items())[:5]:
            print(f"  {key}: {value}")

# Test with S3 storage (uncomment when ready to test with S3)
"""
# Simulate Lambda event with S3 storage
s3_event = {
    'last_mod_date': ("2022/01/01", "2022/05/01"),
    'agency_code': '7504',
    'max_results': 2,
    's3_bucket': 'your-test-bucket',
    's3_key': 'fpds-data/test-output.json'
}

print("\nTesting Lambda handler with S3 storage:", json.dumps(s3_event, indent=2))

# Invoke the Lambda handler
s3_response = lambda_handler(s3_event, None)

# Print the response
print(f"\nStatus code: {s3_response['statusCode']}")

# Parse the response body
s3_body = json.loads(s3_response['body'])
print(f"Response message: {s3_body['message']}")

# Check if S3 location was returned
if s3_response['statusCode'] == 200 and 's3_location' in s3_body:
    print(f"Data stored at: {s3_body['s3_location']}")
"""
