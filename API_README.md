# FPDS API Documentation

## Overview

The FPDS API provides programmatic access to Federal Procurement Data System (FPDS) contract data. It allows users to query contract data by date range, agency code, and other parameters, returning structured JSON data for analysis and integration with other systems.

## Base URL

```
https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds
```

## Authentication

The API is currently publicly accessible and does not require authentication.

## Endpoints

### GET /fpds

Retrieves contract data from the FPDS system based on the provided query parameters.

#### Query Parameters

| Parameter    | Required | Description                                                | Format     | Example     |
|--------------|----------|------------------------------------------------------------|------------|-------------|
| start_date   | Yes      | Start date for last modified date range                    | YYYY/MM/DD | 2023/01/01  |
| end_date     | Yes      | End date for last modified date range                      | YYYY/MM/DD | 2023/01/31  |
| agency_code  | Yes      | Agency code to filter by                                   | String     | 7504        |
| max_results  | No       | Maximum number of results to return (default: 10, max: 100)| Integer    | 5           |
| award_type   | No       | Type of award to filter by                                 | String     | Purchase Order |
| contract_type| No       | Type of contract to filter by                             | String     | IDV         |
| min_value    | No       | Minimum contract value                                     | Number     | 10000       |
| max_value    | No       | Maximum contract value                                     | Number     | 100000      |
| naics_code   | No       | NAICS code to filter by                                   | String     | 541512      |
| title_keyword| No       | Keyword to search in contract titles                      | String     | software    |

##### Valid Award Types
- BPA Call
- Purchase Order
- Delivery Order
- Definitive Contract

##### Valid Contract Types
- IDV (Indefinite Delivery Vehicle)
- Award

#### Response Format

The API returns data in JSON format with the following structure:

```json
{
  "count": 2,
  "data": [
    {
      "title": "Contract title",
      "link": "Link to FPDS details",
      "modified": "Last modified date",
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

#### Response Fields

| Field            | Description                                                |
|------------------|------------------------------------------------------------|
| count            | Number of records returned                                 |
| data             | Array of contract records                                  |
| title            | Contract title                                             |
| link             | URL to view the contract details on the FPDS website       |
| modified         | Last modified date of the contract record                  |
| award_attributes | Object containing detailed contract attributes             |

#### Status Codes

| Status Code | Description                                                |
|-------------|------------------------------------------------------------|
| 200         | Success                                                    |
| 400         | Bad Request - Missing or invalid parameters                |
| 500         | Internal Server Error                                      |

## Examples

### Example 1: Basic Query

Request:
```
GET https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds?start_date=2023/01/01&end_date=2023/01/31&agency_code=7504
```

This will return up to 10 contracts (default) modified between January 1, 2023 and January 31, 2023 for agency code 7504.

### Example 2: Advanced Query with Filters

Request:
```
GET https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds?start_date=2023/01/01&end_date=2023/01/31&agency_code=7504&award_type=Purchase Order&min_value=50000&max_value=100000&title_keyword=software
```

This will return purchase orders with values between $50,000 and $100,000 that have "software" in their titles.

### Example 3: Using with cURL

```bash
curl -X GET "https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds?start_date=2023/01/01&end_date=2023/01/31&agency_code=7504&naics_code=541512&contract_type=Award"
```

### Example 4: Using with Python

```python
import requests
import json

url = "https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds"
params = {
    "start_date": "2023/01/01",
    "end_date": "2023/01/31",
    "agency_code": "7504",
    "award_type": "Purchase Order",
    "min_value": 50000,
    "max_value": 100000,
    "naics_code": "541512",
    "title_keyword": "software"
}

response = requests.get(url, params=params)
data = response.json()

print(f"Found {data['count']} contracts")
for contract in data['data']:
    print(f"Title: {contract['title']}")
    print(f"Value: ${contract['award_attributes'].get('BASE_AND_ALL_OPTIONS_VALUE', 'N/A')}")
    print("---")
```

### Example 5: Using with JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const url = new URL('https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds');
url.searchParams.append('start_date', '2023/01/01');
url.searchParams.append('end_date', '2023/01/31');
url.searchParams.append('agency_code', '7504');
url.searchParams.append('award_type', 'Purchase Order');
url.searchParams.append('min_value', '50000');
url.searchParams.append('max_value', '100000');
url.searchParams.append('naics_code', '541512');
url.searchParams.append('title_keyword', 'software');

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} contracts`);
    data.data.forEach(contract => {
      console.log(`Title: ${contract.title}`);
      console.log(`Value: $${contract.award_attributes['BASE_AND_ALL_OPTIONS_VALUE'] || 'N/A'}`);
      console.log('---');
    });
  })
  .catch(error => console.error('Error:', error));
```

## Common NAICS Codes

Here are some common NAICS codes for IT and professional services:

| NAICS Code | Description                                   |
|------------|-----------------------------------------------|
| 541512     | Computer Systems Design Services              |
| 541511     | Custom Computer Programming Services          |
| 541513     | Computer Facilities Management Services       |
| 541519     | Other Computer Related Services              |
| 541611     | Administrative Management Consulting Services |
| 541618     | Other Management Consulting Services         |

## Error Handling

### Missing Required Parameters

If you omit a required parameter, the API will return a 400 Bad Request response:

```json
{
  "error": "Missing required parameters",
  "missing": ["start_date", "end_date"]
}
```

### Invalid Parameter Values

If you provide an invalid value for a parameter, the API will return a 400 Bad Request response with valid options:

```json
{
  "error": "Invalid award_type",
  "valid_values": ["BPA Call", "Purchase Order", "Delivery Order", "Definitive Contract"]
}
```

### Internal Server Error

If the API encounters an unexpected error, it will return a 500 Internal Server Error response:

```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

The API currently does not implement rate limiting, but excessive usage may be monitored and restricted if necessary.

## Support

For questions or issues with the API, please contact the development team at [your-email@example.com].

## Changelog

### v1.1.0 (2025-03-03)
- Added support for filtering by award type, contract type, and contract value range
- Added support for NAICS code filtering
- Added support for title keyword search
- Updated documentation with new parameters and examples

### v1.0.0 (2025-03-02)
- Initial release of the FPDS API 