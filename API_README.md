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
| 400         | Bad Request - Missing required parameters                  |
| 500         | Internal Server Error                                      |

## Examples

### Example 1: Basic Query

Request:
```
GET https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds?start_date=2023/01/01&end_date=2023/01/31&agency_code=7504
```

This will return up to 10 contracts (default) modified between January 1, 2023 and January 31, 2023 for agency code 7504.

### Example 2: Limiting Results

Request:
```
GET https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds?start_date=2023/01/01&end_date=2023/01/31&agency_code=7504&max_results=2
```

This will return up to 2 contracts modified between January 1, 2023 and January 31, 2023 for agency code 7504.

### Example 3: Using with cURL

```bash
curl -X GET "https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds?start_date=2023/01/01&end_date=2023/01/31&agency_code=7504&max_results=5"
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
    "max_results": 5
}

response = requests.get(url, params=params)
data = response.json()

print(f"Found {data['count']} contracts")
for contract in data['data']:
    print(f"Title: {contract['title']}")
    print(f"Modified: {contract['modified']}")
    print("---")
```

### Example 5: Using with JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const url = new URL('https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds');
url.searchParams.append('start_date', '2023/01/01');
url.searchParams.append('end_date', '2023/01/31');
url.searchParams.append('agency_code', '7504');
url.searchParams.append('max_results', '5');

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} contracts`);
    data.data.forEach(contract => {
      console.log(`Title: ${contract.title}`);
      console.log(`Modified: ${contract.modified}`);
      console.log('---');
    });
  })
  .catch(error => console.error('Error:', error));
```

## Common Agency Codes

Here are some common agency codes that can be used with the API:

| Agency Code | Agency Name                                   |
|-------------|-----------------------------------------------|
| 7504        | Office of the Inspector General               |
| 7500        | Department of Health and Human Services       |
| 9700        | Department of Defense                         |
| 1700        | Department of the Navy                        |
| 1900        | Department of State                           |
| 6900        | Department of Transportation                  |
| 7000        | Department of Homeland Security               |

## Error Handling

### Missing Required Parameters

If you omit a required parameter, the API will return a 400 Bad Request response:

```json
{
  "error": "Missing required parameters",
  "missing": ["start_date", "end_date"]
}
```

### Internal Server Error

If the API encounters an unexpected error, it will return a 500 Internal Server Error response:

```json
{
  "error": "Internal server error",
  "message": "Error details"
}
```

## Rate Limiting

The API currently does not implement rate limiting, but excessive usage may be monitored and restricted if necessary.

## Support

For questions or issues with the API, please contact the development team at [your-email@example.com].

## Changelog

### v1.0.0 (2025-03-02)
- Initial release of the FPDS API 