#!/usr/bin/env python3
"""Debug real Gemini LLM responses"""

from main import create_agent

def debug_real_llm():
    """Debug what the real LLM is generating"""
    agent = create_agent(debug=True)
    
    test_requests = [
        "create folder my_tests",
        "create hello.py with print hello world",
        "run calculator.py",
        "delete test.py",
        "check syntax main.py"
    ]
    
    print("=== DEBUGGING REAL LLM RESPONSES ===\n")
    
    for request in test_requests:
        print(f"Request: {request}")
        print("-" * 50)
        
        # Get the context and reasoning
        context = agent._perceive(request)
        plan = agent._reason(request, context)
        
        print(f"Plan type: {plan.get('type')}")
        print(f"Tool: {plan.get('tool')}")
        print(f"Params: {plan.get('params')}")
        print(f"Raw response: {plan.get('raw_response', 'N/A')}")
        print("=" * 70)
        print()

if __name__ == "__main__":
    debug_real_llm()
