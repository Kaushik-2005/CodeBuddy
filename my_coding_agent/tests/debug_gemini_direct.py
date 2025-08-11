#!/usr/bin/env python3
"""Debug Gemini LLM responses directly"""

import os
from dotenv import load_dotenv
from core.llm_client import GeminiClient

# Load environment variables
load_dotenv()

def debug_gemini_direct():
    """Test Gemini directly with our prompts"""
    
    # Force real API usage
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("No API key found, cannot test real Gemini")
        return
    
    llm = GeminiClient(api_key=api_key)
    
    # Test the exact prompt format our agent uses
    test_prompt = """You are an intelligent coding assistant. Analyze the user's request and respond with the appropriate action.

USER REQUEST: "create folder my_tests"

AVAILABLE TOOLS: read_file, write_file, list_files, create_folder, delete_file, delete_folder, run_python, run_command, check_syntax

RECENT ACTIONS:


INSTRUCTIONS:
1. If the user wants to perform a coding task, respond with a tool command in this format: tool_name(param1="value1", param2="value2")
2. If the user is asking a question or being conversational, respond naturally
3. If you're unsure, ask for clarification

EXAMPLES:
- "show me main.py" → read_file(filepath="main.py")
- "create hello.py" → write_file(filepath="hello.py", content='''print("Hello, World!")''')
- "list files" → list_files(directory=".")
- "hello" → Natural conversational response

IMPORTANT: For write_file, always include both filepath and content parameters with triple quotes for multi-line content.

Respond with either a tool command or natural conversation:"""

    print("Testing real Gemini with our prompt format...")
    print("=" * 60)
    
    try:
        response = llm.generate(test_prompt)
        print(f"Gemini Response: '{response}'")
        print("=" * 60)
        
        # Test our parsing on this response
        from core.agent import CodingAgent
        agent = CodingAgent(llm, debug=True)
        plan = agent._parse_llm_response(response, "create folder my_tests")
        print(f"Parsed Plan: {plan}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_gemini_direct()
