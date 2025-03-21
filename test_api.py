import requests
import urllib.parse

# API Gateway endpoint
base_url = 'https://yf45cj1sk4.execute-api.us-east-1.amazonaws.com/prod/fpds'

# Request parameters
params = {
    "start_date": "2024/04/01",
    "end_date": "2024/06/21",
    "agency_code": "7504",
    "max_results": "100"
}

try:
    # Make the request
    response = requests.get(base_url, params=params, headers={'Accept': 'application/json'})
    
    # Print request details
    print("Request URL:", response.request.url)
    print("Request Headers:", dict(response.request.headers))
    
    # Print response details
    print("\nStatus Code:", response.status_code)
    print("Response Headers:", dict(response.headers))
    print("Response Body:", response.text)
except Exception as e:
    print(f"Error: {str(e)}") 