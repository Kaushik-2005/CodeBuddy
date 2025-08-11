#!/usr/bin/env python3
"""Debug .git folder risk assessment"""

import os
from safety.approval import SafetyApprovalSystem

def debug_git_risk():
    """Debug why .git folder is not assessed as high risk"""
    safety = SafetyApprovalSystem()
    
    folderpath = ".git"
    
    print(f"Testing folder: {folderpath}")
    print(f"Exists: {os.path.exists(folderpath)}")
    print(f"Is directory: {os.path.isdir(folderpath) if os.path.exists(folderpath) else 'N/A'}")
    
    # Test the assessment method directly
    risk = safety._assess_folder_deletion_risk(folderpath=folderpath)
    print(f"Risk level: {risk}")
    
    # Debug the logic
    dirname = os.path.basename(folderpath).lower()
    folderpath_lower = folderpath.lower()
    
    print(f"Directory name: '{dirname}'")
    print(f"Folder path lower: '{folderpath_lower}'")
    
    critical_dirs = [
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        'src', 'lib', 'bin', 'core', 'system'
    ]
    
    print("Checking critical directories:")
    for critical in critical_dirs:
        in_dirname = critical in dirname
        in_folderpath = critical in folderpath_lower
        print(f"  {critical}: in dirname={in_dirname}, in folderpath={in_folderpath}")
        if in_dirname or in_folderpath:
            print(f"    -> Should be HIGH RISK")

if __name__ == "__main__":
    debug_git_risk()
