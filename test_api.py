#!/usr/bin/env python3

import requests
import json

def test_backend():
    base_url = "http://localhost:8000"
    
    # Test bins endpoint
    print("Testing bins endpoint...")
    try:
        response = requests.get(f"{base_url}/bins/")
        print(f"Bins endpoint status: {response.status_code}")
        if response.status_code == 200:
            bins = response.json()
            print(f"Found {len(bins)} bins")
            print(f"First bin: {bins[0] if bins else 'None'}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Bins test failed: {e}")
    
    # Test simulations endpoint
    print("\nTesting simulations endpoint...")
    try:
        response = requests.get(f"{base_url}/simulations/")
        print(f"Simulations endpoint status: {response.status_code}")
        if response.status_code == 200:
            simulations = response.json()
            print(f"Found {len(simulations)} simulations")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Simulations test failed: {e}")
    
    # Test create simulation
    print("\nTesting create simulation...")
    try:
        payload = {
            "name": "API Test",
            "max_trucks": 1,
            "max_capacity": 100,
            "bins_to_collect": 2
        }
        response = requests.post(f"{base_url}/simulations/", json=payload)
        print(f"Create simulation status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Create simulation test failed: {e}")

if __name__ == "__main__":
    test_backend()
