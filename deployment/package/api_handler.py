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
- award_type: (Optional) Type of award (BPA Call, Purchase Order, Delivery Order, Definitive Contract)
- contract_type: (Optional) Type of contract (IDV or Award)
- min_value: (Optional) Minimum contract value
- max_value: (Optional) Maximum contract value
- naics_code: (Optional) NAICS code to filter by
- title_keyword: (Optional) Keyword to search in contract titles

Usage example (API Gateway):
    GET /fpds?start_date=2022/01/01&end_date=2022/05/01&agency_code=7504&max_results=20
"""

import json
import logging
import boto3
from datetime import datetime
from atomreq import fetch_fpds_data
from field_utils import load_fields_config
from data_processor import process_fpds_data

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('fpds_contracts')

def store_in_dynamodb(processed_data):
    """
    Store processed FPDS data in DynamoDB
    """
    with table.batch_writer() as batch:
        for item in processed_data:
            # Extract the contract ID and last modified date
            contract_id = item.get('entry.content.award.awardID.awardContractID.PIID', 
                                 item.get('entry.content.award.awardID.referencedIDVID.PIID', 
                                 f"unknown_{datetime.now().timestamp()}"))
            
            last_modified = item.get('entry.modified', 
                                   item.get('entry.content.award.transactionInformation.lastModifiedDate',
                                   datetime.now().isoformat()))
            
            # Prepare the item for DynamoDB
            dynamo_item = {
                'contract_id': contract_id,
                'last_modified_date': last_modified,
                'data': item
            }
            
            # Write to DynamoDB
            batch.put_item(Item=dynamo_item)

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
        award_type = query_params.get('award_type')
        contract_type = query_params.get('contract_type')
        min_value = query_params.get('min_value')
        max_value = query_params.get('max_value')
        naics_code = query_params.get('naics_code')
        title_keyword = query_params.get('title_keyword')
        
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
        
        # Validate award_type if provided
        if award_type and award_type not in ["BPA Call", "Purchase Order", "Delivery Order", "Definitive Contract"]:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid award_type',
                    'valid_values': ["BPA Call", "Purchase Order", "Delivery Order", "Definitive Contract"]
                })
            }
        
        # Validate contract_type if provided
        if contract_type and contract_type not in ["IDV", "Award"]:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid contract_type',
                    'valid_values': ["IDV", "Award"]
                })
            }
        
        # Format date range for fetch_fpds_data
        last_mod_date = (start_date, end_date)
        
        # Build additional query parameters
        additional_params = {}
        if award_type:
            additional_params['award_type'] = award_type
        if contract_type:
            additional_params['contract_type'] = contract_type
        if min_value and max_value:
            additional_params['value_range'] = (float(min_value), float(max_value))
        if naics_code:
            additional_params['naics_code'] = naics_code
        if title_keyword:
            additional_params['title_keyword'] = title_keyword
        
        # Fetch FPDS data
        logger.info(f"Fetching FPDS data for agency {agency_code} with date range {last_mod_date}")
        data = fetch_fpds_data(last_mod_date, agency_code, max_results, additional_params=additional_params)
        
        # Process data with field configuration
        fields_config = load_fields_config()
        processed_data = process_fpds_data(data, fields_config)
        
        # Store in DynamoDB
        store_in_dynamodb(processed_data)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'FPDS data processed and stored in DynamoDB successfully',
                'count': len(processed_data),
                'data': processed_data
            })
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
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