#!/usr/bin/env python3
"""Test Git tools integration"""

from main import create_agent

def test_git_tools():
    """Test Git tools with the agent"""
    
    # Create agent
    agent = create_agent(debug=True)
    
    print("=== TESTING GIT TOOLS INTEGRATION ===\n")
    
    test_requests = [
        "git status",
        "git diff",
        "git log",
        "git branch",
        "git add main.py",
        "git commit 'Test commit message'",
    ]
    
    for request in test_requests:
        print(f"Request: {request}")
        print("-" * 50)
        
        try:
            result = agent.process_request(request)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("=" * 70)
        print()

def test_git_tools_direct():
    """Test Git tools directly"""
    from tools.git_tools import GitStatusTool, GitDiffTool, GitLogTool
    
    print("\n=== TESTING GIT TOOLS DIRECTLY ===\n")
    
    # Test Git status
    print("1. Testing Git Status:")
    git_status = GitStatusTool()
    result = git_status.execute()
    print(result)
    print("-" * 50)
    
    # Test Git diff
    print("2. Testing Git Diff:")
    git_diff = GitDiffTool()
    result = git_diff.execute()
    print(result)
    print("-" * 50)
    
    # Test Git log
    print("3. Testing Git Log:")
    git_log = GitLogTool()
    result = git_log.execute(count=5)
    print(result)
    print("-" * 50)

if __name__ == "__main__":
    test_git_tools()
    test_git_tools_direct()
