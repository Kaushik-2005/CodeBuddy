#!/usr/bin/env python3
"""Debug parameter parsing"""

from main import create_agent

def debug_params():
    """Debug parameter parsing"""
    agent = create_agent(debug=True)
    
    # Test parameter parsing directly
    test_cases = [
        'filepath="hello.py", content="""print("Hello, World!")"""',
        'filepath="hello.py", content="print(\'Hello\')"',
        'filepath="test.py"'
    ]
    
    for test_case in test_cases:
        print(f"Input: {test_case}")
        parsed = agent._parse_tool_params(test_case)
        print(f"Parsed: {parsed}")
        print("-" * 50)

if __name__ == "__main__":
    debug_params()
