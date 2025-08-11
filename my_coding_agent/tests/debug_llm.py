#!/usr/bin/env python3
"""Debug LLM responses"""

from core.llm_client import GeminiClient

def debug_llm():
    """Debug LLM mock responses"""
    llm = GeminiClient()
    
    test_prompts = [
        "create hello.py with print hello world",
        "write a file called test.py",
        "make a new file hello.py",
        "show me main.py"
    ]
    
    for prompt in test_prompts:
        print(f"Prompt: {prompt}")
        response = llm._mock_response(prompt)
        print(f"Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    debug_llm()
