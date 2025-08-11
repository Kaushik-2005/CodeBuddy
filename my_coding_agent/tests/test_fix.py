#!/usr/bin/env python3
"""Test the file creation fix"""

from core.llm_client import GeminiClient
from core.agent import CodingAgent
from main import create_agent

def test_llm_response():
    """Test LLM response generation"""
    print("Testing LLM response...")
    llm = GeminiClient()
    response = llm.generate("create hello.py to print hello world")
    print(f"LLM Response: {response}")
    return response

def test_parameter_parsing():
    """Test parameter parsing"""
    print("\nTesting parameter parsing...")
    agent = create_agent()
    
    # Test the parameter parsing directly
    test_params = 'filepath="hello.py", content="""print("Hello, World!")"""'
    parsed = agent._parse_tool_params(test_params)
    print(f"Parsed params: {parsed}")
    return parsed

def test_full_flow():
    """Test the full flow"""
    print("\nTesting full flow...")
    agent = create_agent()
    result = agent.process_request("create hello.py to print hello world")
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    test_llm_response()
    test_parameter_parsing()
    test_full_flow()
