#!/usr/bin/env python3
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
