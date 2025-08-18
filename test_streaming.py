#!/usr/bin/env python3

import requests
import json

# Test the agentic-chat agent streaming
def test_streaming():
    url = "http://localhost:8003/invoke"
    
    # Create a streaming test request
    test_request = {
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Tell me a story about a robot learning to dance"
                }
            ]
        },
        "session_id": "test-streaming-session-456",
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing agentic-chat agent streaming...")
    print(f"Request: {json.dumps(test_request, indent=2)}")
    
    try:
        response = requests.post(url, json=test_request, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("metadata", {}).get("streaming"):
                print("✅ Streaming agent is working!")
            else:
                print("⚠️  Agent working but streaming flag not set")
        else:
            print("❌ Agent returned an error")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_streaming()
