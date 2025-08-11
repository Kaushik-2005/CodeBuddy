#!/usr/bin/env python3
"""Debug agent reasoning"""

from main import create_agent

def debug_agent_reasoning():
    """Debug the agent reasoning process"""
    agent = create_agent(debug=True)  # Enable debug mode
    
    print("=== DEBUGGING AGENT REASONING ===")
    
    # Test with a write request
    user_input = "create hello.py with print hello world"
    print(f"User input: {user_input}")
    
    # Step 1: Test LLM response
    context = agent._perceive(user_input)
    print(f"Context: {context}")
    
    # Step 2: Test reasoning
    plan = agent._reason(user_input, context)
    print(f"Plan: {plan}")
    
    # Step 3: Test action
    result = agent._act(plan, user_input)
    print(f"Result: {result}")

if __name__ == "__main__":
    debug_agent_reasoning()
