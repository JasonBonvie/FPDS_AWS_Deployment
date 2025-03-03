# FPDS Data Processing System

This system retrieves and processes data from the Federal Procurement Data System (FPDS) ATOM feed. It can be deployed as an AWS Lambda function with API Gateway integration to provide a RESTful API for accessing FPDS data.

## Features

- Fetches data from the FPDS ATOM feed with pagination support
- Processes and validates field values
- Provides both Lambda function and API Gateway integration
- Includes comprehensive test scripts
- Supports deployment to AWS Lambda

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
└── tests/                  # Test scripts
    ├── test_processor.py   # Tests for data processing
    ├── test_lambda.py      # Tests for Lambda handler
    └── test_api.py         # Tests for API Gateway handler
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Testing

Run the test scripts to verify functionality:

```
python tests/test_processor.py
python tests/test_lambda.py
python tests/test_api.py
```

## Deployment

### Prepare Deployment Package

Run the deployment script to create a Lambda deployment package:

```
./deploy.sh
```

This will create a zip file at `deployment/lambda_package.zip` containing all necessary files.

### Deploy to AWS Lambda

#### Option 1: Direct Lambda Function

```
aws lambda create-function --function-name fpds-data-processor \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --role YOUR_LAMBDA_EXECUTION_ROLE_ARN \
  --zip-file fileb://deployment/lambda_package.zip
```

#### Option 2: API Gateway Integration

```
aws lambda create-function --function-name fpds-api \
  --runtime python3.11 \
  --handler api_handler.api_handler \
  --role YOUR_LAMBDA_EXECUTION_ROLE_ARN \
  --zip-file fileb://deployment/lambda_package.zip
```

### Set Up API Gateway

1. Create a new REST API in API Gateway
2. Create a resource (e.g., `/fpds`)
3. Create a GET method for the resource
4. Configure the integration type as "Lambda Function"
5. Select the `fpds-api` Lambda function
6. Deploy the API to a stage (e.g., "prod")

## API Usage

Once deployed, you can access the API using the following endpoint:

```
GET https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/fpds?start_date=2023/01/01&end_date=2023/01/31&agency_code=7504&max_results=50
```

### Query Parameters

- `start_date`: Start date for last modified date range (YYYY/MM/DD)
- `end_date`: End date for last modified date range (YYYY/MM/DD)
- `agency_code`: Agency code to filter by
- `max_results`: (Optional) Maximum number of results to return (default: 10)

### Response Format

```json
{
  "count": 30,
  "data": [
    {
      "title": "Contract Award",
      "link": "https://www.fpds.gov/ezsearch/...",
      "modified": "2023-01-15T12:34:56Z",
      "award_attributes": {
        "key1": "value1",
        "key2": "value2",
        ...
      }
    },
    ...
  ]
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 