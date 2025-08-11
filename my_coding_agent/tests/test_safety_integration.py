#!/usr/bin/env python3
"""Test safety system integration with agent"""

from main import create_agent
from interface.cli import CLI

def test_safety_integration():
    """Test safety system integration"""
    
    # Create CLI and agent with safety system
    cli = CLI("TestAgent")
    agent = create_agent(debug=True, cli_interface=cli)
    
    print("=== TESTING SAFETY INTEGRATION ===\n")
    
    # Test safe operations (should not require approval)
    print("1. Testing SAFE operation (read file):")
    result = agent.process_request("show me main.py")
    print(f"Result: {result[:100]}...\n")
    
    # Test operations that require approval (but we'll simulate approval)
    print("2. Testing operations that would require approval:")
    
    # Test file deletion risk assessment
    safety_system = agent._get_safety_system()
    
    test_operations = [
        ("delete_file", {"filepath": "test.txt"}, "Delete test file"),
        ("delete_file", {"filepath": "main.py"}, "Delete main.py (critical)"),
        ("delete_folder", {"folderpath": ".git"}, "Delete .git folder (critical)"),
        ("run_command", {"command": "ls -la"}, "List files command"),
        ("run_command", {"command": "rm -rf /"}, "Dangerous command"),
    ]
    
    for operation, params, description in test_operations:
        risk_level = safety_system.assess_risk(operation, **params)
        requires_approval = safety_system.requires_approval(operation, **params)
        
        print(f"Operation: {description}")
        print(f"Risk Level: {risk_level.value}")
        print(f"Requires Approval: {requires_approval}")
        print("-" * 40)

def test_mock_approval():
    """Test with mock approval responses"""
    from safety.approval import SafetyApprovalSystem
    
    # Create a mock CLI that always approves
    class MockCLI:
        def ask_approval(self, message, risk_level=None, warnings=None, details=None, default=False):
            print(f"MOCK APPROVAL REQUEST: {message}")
            if risk_level:
                print(f"Risk Level: {risk_level.value}")
            if warnings:
                for warning in warnings:
                    print(f"Warning: {warning}")
            print("MOCK: Approving operation")
            return True
    
    # Test with mock CLI
    mock_cli = MockCLI()
    agent = create_agent(debug=True, cli_interface=mock_cli)
    
    print("\n=== TESTING WITH MOCK APPROVAL ===\n")
    
    # This should trigger approval request
    print("Testing file deletion (should request approval):")
    result = agent.process_request("delete test.py")
    print(f"Result: {result}")

if __name__ == "__main__":
    test_safety_integration()
    test_mock_approval()
