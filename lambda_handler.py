"""
AWS Lambda Handler for FPDS Data Processing

This module provides the AWS Lambda handler function for processing FPDS data.
It integrates the FPDS data retrieval, field validation, and data processing
functionality into a serverless function that can be deployed to AWS Lambda.

Key features:
- Handles Lambda event parameters for FPDS data retrieval
- Validates input parameters
- Fetches and processes FPDS data
- Supports storing results in S3 or returning directly in the response
- Provides proper error handling and status codes

Main function:
- lambda_handler: AWS Lambda handler function

The Lambda function expects an event object with the following parameters:
- last_mod_date: Tuple of (start_date, end_date) for last modified date range
- agency_code: Agency code to filter by
- max_results: (Optional) Maximum number of results to return
- s3_bucket: (Optional) S3 bucket for storing results
- s3_key: (Optional) S3 key for storing results

Usage example (AWS Lambda):
    {
        "last_mod_date": ["2022/01/01", "2022/05/01"],
        "agency_code": "7504",
        "max_results": 20,
        "s3_bucket": "my-bucket",
        "s3_key": "fpds-data/results.json"
    }
"""

import json
import os
from atomreq import fetch_fpds_data
from field_utils import load_fields_config
from data_processor import process_fpds_data

def lambda_handler(event, context):
    """
    AWS Lambda handler for FPDS data processing.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        dict: Lambda response
    """
    try:
        # Extract parameters from event
        last_mod_date = event.get('last_mod_date')
        agency_code = event.get('agency_code')
        max_results = event.get('max_results', 5)
        
        # Validate required parameters
        if not last_mod_date or not agency_code:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing required parameters: last_mod_date and agency_code are required'
                })
            }
        
        # Load field configuration
        fields_config = load_fields_config()
        
        # Fetch FPDS data
        data = fetch_fpds_data(last_mod_date, agency_code, max_results)
        
        # Process data with field configuration
        processed_data = process_fpds_data(data, fields_config)
        
        # Check if S3 storage is requested
        s3_bucket = event.get('s3_bucket')
        s3_key = event.get('s3_key')
        
        if s3_bucket and s3_key:
            try:
                # Import boto3 only when needed to reduce cold start time
                import boto3
                
                # Create S3 client
                s3_client = boto3.client('s3')
                
                # Upload to S3
                s3_client.put_object(
                    Bucket=s3_bucket,
                    Key=s3_key,
                    Body=json.dumps(processed_data)
                )
                
                # Return S3 location
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'FPDS data processed and stored in S3',
                        's3_location': f"s3://{s3_bucket}/{s3_key}"
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'message': f"Error storing data in S3: {str(e)}"
                    })
                }
        else:
            # Return data directly
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'FPDS data processed successfully',
                    'data': processed_data
                })
            }
    except Exception as e:
        # Log the error
        print(f"Error processing FPDS data: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error processing FPDS data: {str(e)}"
            })
        }
