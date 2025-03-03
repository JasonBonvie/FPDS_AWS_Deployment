#!/bin/bash
# =============================================================================
# FPDS Lambda Deployment Script
# =============================================================================
#
# This script creates a deployment package for the FPDS data processing Lambda function.
# It installs dependencies, copies source files, and creates a zip file that can be
# deployed to AWS Lambda with API Gateway integration.
#
# The deployment package includes:
# - Python source files (atomreq.py, field_utils.py, data_processor.py, lambda_handler.py, api_handler.py)
# - Configuration files (fields.json)
# - Dependencies (requests, boto3)
#
# Usage:
#   ./deploy.sh
#
# After running this script, you can deploy the Lambda function using the AWS CLI:
#   aws lambda create-function --function-name fpds-data-processor \
#     --runtime python3.11 \
#     --handler lambda_handler.lambda_handler \
#     --role YOUR_LAMBDA_EXECUTION_ROLE_ARN \
#     --zip-file fileb://deployment/lambda_package.zip
#
# For API Gateway integration, deploy with:
#   aws lambda create-function --function-name fpds-api \
#     --runtime python3.11 \
#     --handler api_handler.api_handler \
#     --role YOUR_LAMBDA_EXECUTION_ROLE_ARN \
#     --zip-file fileb://deployment/lambda_package.zip
#
# Then create an API Gateway REST API and integrate it with the Lambda function.
# =============================================================================

# Create a temporary directory
mkdir -p deployment/package

# Install dependencies
pip install -r requirements.txt -t deployment/package

# Copy source files
cp atomreq.py deployment/package/
cp field_utils.py deployment/package/
cp data_processor.py deployment/package/
cp lambda_handler.py deployment/package/
cp api_handler.py deployment/package/
cp fields.json deployment/package/

# Create zip file
cd deployment/package
zip -r ../lambda_package.zip .
cd ../..

# Print package size
echo "Deployment package created: deployment/lambda_package.zip"
ls -lh deployment/lambda_package.zip

echo "To deploy to AWS Lambda, use:"
echo "aws lambda create-function --function-name fpds-data-processor \\"
echo "  --runtime python3.11 \\"
echo "  --handler lambda_handler.lambda_handler \\"
echo "  --role YOUR_LAMBDA_EXECUTION_ROLE_ARN \\"
echo "  --zip-file fileb://deployment/lambda_package.zip"

echo ""
echo "For API Gateway integration, deploy with:"
echo "aws lambda create-function --function-name fpds-api \\"
echo "  --runtime python3.11 \\"
echo "  --handler api_handler.api_handler \\"
echo "  --role YOUR_LAMBDA_EXECUTION_ROLE_ARN \\"
echo "  --zip-file fileb://deployment/lambda_package.zip" 