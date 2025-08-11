#!/usr/bin/env python3
"""Test the safety approval system"""

from safety.approval import SafetyApprovalSystem, RiskLevel

def test_risk_assessment():
    """Test risk assessment for various operations"""
    safety = SafetyApprovalSystem()
    
    print("=== TESTING RISK ASSESSMENT ===\n")
    
    test_cases = [
        # File operations
        ("delete_file", {"filepath": "test.txt"}, "Low risk file"),
        ("delete_file", {"filepath": "main.py"}, "High risk file"),
        ("delete_file", {"filepath": "nonexistent.txt"}, "Non-existent file"),
        
        # Folder operations
        ("delete_folder", {"folderpath": "temp_folder"}, "Empty folder"),
        ("delete_folder", {"folderpath": ".git"}, "Critical folder"),
        
        # Commands
        ("run_command", {"command": "ls -la"}, "Safe command"),
        ("run_command", {"command": "rm -rf /"}, "Critical command"),
        ("run_command", {"command": "sudo apt install"}, "High risk command"),
        
        # Safe operations
        ("read_file", {"filepath": "main.py"}, "Safe read"),
        ("list_files", {"directory": "."}, "Safe list"),
    ]
    
    for operation, params, description in test_cases:
        risk = safety.assess_risk(operation, **params)
        requires_approval = safety.requires_approval(operation, **params)
        
        print(f"Operation: {operation}")
        print(f"Description: {description}")
        print(f"Parameters: {params}")
        print(f"Risk Level: {risk.value}")
        print(f"Requires Approval: {requires_approval}")
        print("-" * 50)

def test_approval_request_creation():
    """Test approval request creation"""
    safety = SafetyApprovalSystem()
    
    print("\n=== TESTING APPROVAL REQUEST CREATION ===\n")
    
    # Test critical command
    request = safety._create_approval_request(
        "run_command", 
        RiskLevel.CRITICAL, 
        command="rm -rf /important_data"
    )
    
    print("Critical Command Request:")
    print(f"Operation: {request.operation}")
    print(f"Description: {request.description}")
    print(f"Risk Level: {request.risk_level.value}")
    print(f"Warnings: {request.warnings}")
    print("-" * 50)
    
    # Test file deletion
    request = safety._create_approval_request(
        "delete_file",
        RiskLevel.HIGH,
        filepath="main.py"
    )
    
    print("File Deletion Request:")
    print(f"Operation: {request.operation}")
    print(f"Description: {request.description}")
    print(f"Risk Level: {request.risk_level.value}")
    print(f"Warnings: {request.warnings}")

def test_console_approval():
    """Test console approval (interactive)"""
    safety = SafetyApprovalSystem()
    
    print("\n=== TESTING CONSOLE APPROVAL (INTERACTIVE) ===\n")
    print("This will test the console approval system.")
    print("You can test different responses.\n")
    
    # Test low risk operation
    print("Testing LOW RISK operation:")
    approved = safety.request_approval("delete_file", filepath="test.txt")
    print(f"Result: {'Approved' if approved else 'Denied'}\n")
    
    # Test high risk operation
    print("Testing HIGH RISK operation:")
    approved = safety.request_approval("delete_file", filepath="main.py")
    print(f"Result: {'Approved' if approved else 'Denied'}\n")

if __name__ == "__main__":
    test_risk_assessment()
    test_approval_request_creation()
    
    # Uncomment to test interactive approval
    # test_console_approval()
