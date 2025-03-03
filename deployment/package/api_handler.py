"""
FPDS API Gateway Handler

This module provides the AWS Lambda handler function for processing FPDS data
through API Gateway requests. It integrates with the existing FPDS data retrieval
and processing functionality to provide a RESTful API interface.

Key features:
- Handles API Gateway event format
- Parses query parameters for FPDS data retrieval
- Validates input parameters
- Returns properly formatted API responses
- Supports CORS for cross-origin requests

Main function:
- api_handler: AWS Lambda handler function for API Gateway events

The API expects the following query parameters:
- start_date: Start date for last modified date range (YYYY/MM/DD)
- end_date: End date for last modified date range (YYYY/MM/DD)
- agency_code: Agency code to filter by
- max_results: (Optional) Maximum number of results to return (default: 10)

Usage example (API Gateway):
    GET /fpds?start_date=2022/01/01&end_date=2022/05/01&agency_code=7504&max_results=20
"""

import json
import logging
from atomreq import fetch_fpds_data
from field_utils import load_fields_config
from data_processor import process_fpds_data

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def api_handler(event, context):
    """
    Lambda handler for API Gateway requests to fetch FPDS data.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with FPDS data
    """
    logger.info("Received API Gateway event: %s", json.dumps(event))
    
    # Get query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    
    # Extract and validate parameters
    try:
        # Required parameters
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        agency_code = query_params.get('agency_code')
        
        # Optional parameters
        max_results = int(query_params.get('max_results', 10))
        
        # Validate required parameters
        if not all([start_date, end_date, agency_code]):
            missing = []
            if not start_date: missing.append('start_date')
            if not end_date: missing.append('end_date')
            if not agency_code: missing.append('agency_code')
            
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required parameters',
                    'missing': missing
                })
            }
        
        # Format date range for fetch_fpds_data
        last_mod_date = (start_date, end_date)
        
        # Fetch FPDS data
        logger.info(f"Fetching FPDS data for agency {agency_code} with date range {last_mod_date}")
        data = fetch_fpds_data(last_mod_date, agency_code, max_results)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'count': len(data),
                'data': data
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handle_options(event):
    """
    Handle OPTIONS requests for CORS preflight
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': ''
    } 