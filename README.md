# FPDS Data Processing System

This system retrieves and processes data from the Federal Procurement Data System (FPDS) ATOM feed and stores it in Amazon DynamoDB. It is deployed as an AWS Lambda function with API Gateway integration to provide a RESTful API for accessing FPDS data.

## Features

- Fetches data from the FPDS ATOM feed with pagination support
- Processes and validates field values
- Stores contract data in Amazon DynamoDB for persistence
- Provides both Lambda function and API Gateway integration
- Includes comprehensive test scripts
- Supports deployment to AWS Lambda
- Extracts and stores contract IDs for easy reference
- Handles various contract types (BPA Calls, Delivery Orders, Purchase Orders, etc.)

## Project Structure

```
.
├── atomreq.py              # Core module for fetching FPDS data
├── field_utils.py          # Utilities for field validation and formatting
├── data_processor.py       # Data processing functionality
├── lambda_handler.py       # AWS Lambda handler for direct invocation
├── api_handler.py          # AWS Lambda handler for API Gateway integration
├── fields.json             # Field configuration
├── requirements.txt        # Python dependencies
├── deploy.sh               # Deployment script
├── API_README.md          # API documentation
├── test_api.py            # API testing script
└── tests/                 # Test scripts
    ├── test_processor.py  # Tests for data processing
    └── test_lambda.py     # Tests for Lambda handler
```

## Prerequisites

- Python 3.11 or higher
- AWS Account with appropriate permissions
- AWS CLI configured with your credentials
- DynamoDB table named `fpds_contracts` created in your AWS account

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure AWS credentials:
   ```
   aws configure
   ```

## DynamoDB Setup

1. Create the DynamoDB table:
   ```
   aws dynamodb create-table \
     --table-name fpds_contracts \
     --attribute-definitions AttributeName=contract_id,AttributeType=S \
     --key-schema AttributeName=contract_id,KeyType=HASH \
     --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
   ```

2. Verify table creation:
   ```
   aws dynamodb describe-table --table-name fpds_contracts
   ```

## Testing

1. Configure test parameters in `test_api.py`:
   ```python
   params = {
       "start_date": "YYYY/MM/DD",
       "end_date": "YYYY/MM/DD",
       "agency_code": "7504",
       "max_results": "100"
   }
   ```

2. Run the test script:
   ```
   python test_api.py
   ```

## Deployment

### Required AWS Resources

1. Lambda Function
2. API Gateway
3. DynamoDB Table
4. IAM Role with permissions for:
   - Lambda execution
   - DynamoDB read/write
   - CloudWatch Logs

### Deploy to AWS Lambda

1. Create the Lambda function:
   ```
   aws lambda create-function --function-name fpds-api \
     --runtime python3.11 \
     --handler api_handler.api_handler \
     --role YOUR_LAMBDA_EXECUTION_ROLE_ARN \
     --timeout 30 \
     --memory-size 256 \
     --zip-file fileb://deployment/lambda_package.zip
   ```

2. Update function configuration if needed:
   ```
   aws lambda update-function-configuration \
     --function-name fpds-api \
     --timeout 30 \
     --memory-size 256
   ```

## API Usage

### Endpoint

```
GET https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds
```

### Query Parameters

Required:
- `start_date`: Start date for last modified date range (YYYY/MM/DD)
- `end_date`: End date for last modified date range (YYYY/MM/DD)
- `agency_code`: Agency code to filter by (e.g., "7504")

Optional:
- `max_results`: Maximum number of results to return (default: 10)
- `award_type`: Filter by award type ("BPA Call", "Purchase Order", "Delivery Order", "Definitive Contract")
- `contract_type`: Filter by contract type ("IDV" or "Award")
- `min_value`: Minimum contract value
- `max_value`: Maximum contract value
- `naics_code`: NAICS code to filter by
- `title_keyword`: Keyword to search in contract titles

### Response Format

```json
{
  "message": "FPDS data processed and stored in DynamoDB successfully",
  "count": 82,
  "data": [
    {
      "title": "Contract Title",
      "link": "https://www.fpds.gov/ezsearch/...",
      "modified": "2024-03-21T14:30:00Z"
    }
  ]
}
```

## Viewing Data in DynamoDB

1. Access the AWS Console: https://console.aws.amazon.com
2. Navigate to DynamoDB service
3. Click on "Tables" in the left sidebar
4. Select the `fpds_contracts` table
5. Click "Explore table items" to view the data
6. Use the search/filter options to find specific contracts

### Data Structure in DynamoDB

Each item in the table contains:
- `contract_id`: Unique identifier extracted from the contract title
- `last_modified_date`: When the contract was last modified
- `data`: Object containing contract details (title, link, modified date)

## Troubleshooting

1. Check CloudWatch Logs for Lambda function errors
2. Verify API Gateway configuration
3. Ensure DynamoDB table exists and has correct permissions
4. Check Lambda function timeout and memory settings
5. Verify IAM roles have necessary permissions

## License

This project is licensed under the MIT License - see the LICENSE file for details. 