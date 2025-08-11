#!/usr/bin/env python3
"""Test real Gemini with various requests"""

from main import create_agent

def test_real_gemini():
    """Test real Gemini with various requests"""
    
    # Force real API usage
    agent = create_agent(debug=True)
    
    test_requests = [
        "create folder my_tests",
        "create hello_world.py with print hello world",
        "run calculator.py",
        "list files",
        "delete test.py"
    ]
    
    print("=== TESTING REAL GEMINI RESPONSES ===\n")
    
    for request in test_requests:
        print(f"Request: {request}")
        print("-" * 50)
        
        try:
            result = agent.process_request(request)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("=" * 70)
        print()

if __name__ == "__main__":
    test_real_gemini()
