#!/usr/bin/env python3

import requests
import json

# Test the agentic-chat agent
def test_agentic_chat():
    url = "http://localhost:8003/invoke"
    
    # Create a simple test request
    test_request = {
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hello! Can you tell me a short joke?"
                }
            ]
        },
        "session_id": "test-session-123",
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing agentic-chat agent...")
    print(f"Request: {json.dumps(test_request, indent=2)}")
    
    try:
        response = requests.post(url, json=test_request, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Agent is working!")
        else:
            print("❌ Agent returned an error")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_agentic_chat()
