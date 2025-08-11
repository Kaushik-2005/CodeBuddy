#!/usr/bin/env python3
"""Test calculator creation"""

from main import create_agent

def test_calculator():
    """Test calculator creation"""
    agent = create_agent(debug=True)
    result = agent.process_request('create calculator.py with basic math functions')
    print('Result:', result)

if __name__ == "__main__":
    test_calculator()
