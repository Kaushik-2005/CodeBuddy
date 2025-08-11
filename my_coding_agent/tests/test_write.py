#!/usr/bin/env python3
"""Test write file functionality"""

from main import create_agent

def test_write_file():
    """Test write file directly"""
    agent = create_agent()
    
    # Test the tool directly
    print("Testing write_file tool directly...")
    result = agent.tools['write_file'](filepath="test.py", content='print("Hello, World!")')
    print(f"Direct tool result: {result}")
    
    # Test through agent reasoning
    print("\nTesting through agent reasoning...")
    result = agent.process_request("write a file called test2.py with hello world")
    print(f"Agent result: {result}")

if __name__ == "__main__":
    test_write_file()
