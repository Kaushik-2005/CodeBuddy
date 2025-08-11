#!/usr/bin/env python3
"""Test new features: folders, deletion, code execution"""

from main import create_agent

def test_new_features():
    """Test all new features"""
    agent = create_agent(debug=True)
    
    print("=== TESTING NEW FEATURES ===\n")
    
    # Test 1: Create folder
    print("1. Testing folder creation...")
    result = agent.process_request("create folder test_folder")
    print(f"Result: {result}\n")
    
    # Test 2: Run Python file
    print("2. Testing Python execution...")
    result = agent.process_request("run hello.py")
    print(f"Result: {result}\n")
    
    # Test 3: Check syntax
    print("3. Testing syntax check...")
    result = agent.process_request("check syntax calculator.py")
    print(f"Result: {result}\n")
    
    # Test 4: Delete file (this should require approval)
    print("4. Testing file deletion...")
    result = agent.process_request("delete hello.py")
    print(f"Result: {result}\n")
    
    # Test 5: Run command
    print("5. Testing command execution...")
    result = agent.process_request("run command dir")
    print(f"Result: {result}\n")

if __name__ == "__main__":
    test_new_features()
