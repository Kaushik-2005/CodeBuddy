#!/usr/bin/env python3
"""Test analysis tools integration"""

from main import create_agent

def test_analysis_tools():
    """Test analysis tools with the agent"""
    
    # Create agent
    agent = create_agent(debug=True)
    
    print("=== TESTING ANALYSIS TOOLS INTEGRATION ===\n")
    
    test_requests = [
        "lint main.py",
        "analyze complexity main.py",
        "security scan main.py",
        "analyze dependencies",
        "code quality main.py",
    ]
    
    for request in test_requests:
        print(f"Request: {request}")
        print("-" * 50)
        
        try:
            result = agent.process_request(request)
            print(f"Result: {result[:500]}...")  # Truncate for readability
        except Exception as e:
            print(f"Error: {e}")
        
        print("=" * 70)
        print()

def test_analysis_tools_direct():
    """Test analysis tools directly"""
    from tools.analysis_tools import PythonLinterTool, ComplexityAnalyzerTool, SecurityScannerTool
    from tools.security_tools import DependencyAnalyzerTool
    
    print("\n=== TESTING ANALYSIS TOOLS DIRECTLY ===\n")
    
    # Test Python linter
    print("1. Testing Python Linter:")
    linter = PythonLinterTool()
    result = linter.execute("main.py")
    print(result[:300] + "..." if len(result) > 300 else result)
    print("-" * 50)
    
    # Test complexity analyzer
    print("2. Testing Complexity Analyzer:")
    complexity = ComplexityAnalyzerTool()
    result = complexity.execute("main.py")
    print(result[:300] + "..." if len(result) > 300 else result)
    print("-" * 50)
    
    # Test security scanner
    print("3. Testing Security Scanner:")
    security = SecurityScannerTool()
    result = security.execute("main.py")
    print(result[:300] + "..." if len(result) > 300 else result)
    print("-" * 50)
    
    # Test dependency analyzer
    print("4. Testing Dependency Analyzer:")
    deps = DependencyAnalyzerTool()
    result = deps.execute()
    print(result[:300] + "..." if len(result) > 300 else result)
    print("-" * 50)

def create_test_file():
    """Create a test file with various issues for analysis"""
    test_code = '''#!/usr/bin/env python3
"""Test file with various code issues"""

import os
import random  # Weak random for security
import pickle

# Hardcoded secret (security issue)
API_KEY = "sk-1234567890abcdef"

def very_long_function_with_many_parameters(param1, param2, param3, param4, param5, param6, param7):
    """This function has too many parameters and will be too long"""
    
    # TODO: Fix this later
    print("Debug statement")  # Debug code
    
    # Long line that exceeds 100 characters - this is a style issue that should be detected by the linter
    
    if param1:
        if param2:
            if param3:
                if param4:  # Deep nesting - complexity issue
                    if param5:
                        result = param1 + param2 + param3 + param4 + param5
                        
    # Bare except clause
    try:
        risky_operation()
    except:
        pass
    
    # SQL injection risk
    query = "SELECT * FROM users WHERE id = %s" % param1
    
    # Command injection risk
    os.system("ls " + param1)
    
    # Pickle security risk
    data = pickle.loads(param2)
    
    # Eval usage
    result = eval(param3)
    
    return result

def risky_operation():
    """Function that might fail"""
    pass

# More functions to increase complexity
def function1(): pass
def function2(): pass
def function3(): pass
def function4(): pass
def function5(): pass
def function6(): pass
def function7(): pass
def function8(): pass
def function9(): pass
def function10(): pass
'''
    
    with open('test_analysis_file.py', 'w') as f:
        f.write(test_code)
    
    print("Created test_analysis_file.py for analysis testing")

if __name__ == "__main__":
    create_test_file()
    test_analysis_tools_direct()
    test_analysis_tools()
