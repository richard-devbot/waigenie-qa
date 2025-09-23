import requests
import json
import time

# Test the pipeline endpoint
url = "http://localhost:8000/api/v1/pipeline/start"

# Test data
payload = {
    "raw_story": "as a user i want to login into https://www.saucedemo.com/ with user name \"standard_user\", password \"secret_sauce\" and add this product to cart \"Sauce Labs Bolt T-Shirt\"",
    "framework": "Playwright (Python)",
    "provider": "Google",
    "model": "gemini-2.0-flash"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if "task_id" in result:
        task_id = result["task_id"]
        print(f"Task ID: {task_id}")
        
        # Test status endpoint
        status_url = f"http://localhost:8000/api/v1/pipeline/status/{task_id}"
        time.sleep(2)  # Wait a bit for the pipeline to start
        
        status_response = requests.get(status_url)
        print(f"Status Code: {status_response.status_code}")
        print(f"Status Response: {status_response.json()}")
        
except Exception as e:
    print(f"Error: {e}")