#!/usr/bin/env python3

print("Hello, testing...")

import requests
print("Requests imported successfully")

try:
    response = requests.get("http://localhost:8000/bins/")
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Number of bins: {len(data)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

print("Test completed")
