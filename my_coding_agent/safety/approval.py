"""
Safety Approval System - User confirmation for destructive operations
"""
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class RiskLevel(Enum):
    """Risk levels for operations"""
    SAFE = "safe"           # No approval needed
    LOW = "low"             # Simple confirmation
    MEDIUM = "medium"       # Detailed confirmation with preview
    HIGH = "high"           # Strong warning with multiple confirmations
    CRITICAL = "critical"   # Maximum warnings, requires typing confirmation


@dataclass
class ApprovalRequest:
    """Request for user approval"""
    operation: str
    description: str
    risk_level: RiskLevel
    details: Dict[str, Any]
    preview: Optional[str] = None
    warnings: Optional[list] = None


class SafetyApprovalSystem:
    """Manages safety approvals for destructive operations"""
    
    def __init__(self, cli_interface=None):
        self.cli = cli_interface
        self.approval_history = []
        
        # Risk assessment rules
        self.risk_rules = {
            # File operations
            'delete_file': self._assess_file_deletion_risk,
            'delete_folder': self._assess_folder_deletion_risk,
            'write_file': self._assess_file_write_risk,

            # Command execution
            'run_command': self._assess_command_risk,

            # Git operations
            'git_status': lambda **kwargs: RiskLevel.SAFE,
            'git_diff': lambda **kwargs: RiskLevel.SAFE,
            'git_log': lambda **kwargs: RiskLevel.SAFE,
            'git_add': lambda **kwargs: RiskLevel.LOW,
            'git_commit': self._assess_git_commit_risk,
            'git_push': self._assess_git_push_risk,
            'git_pull': self._assess_git_pull_risk,
            'git_branch': self._assess_git_branch_risk,

            # Analysis operations (all safe - read-only)
            'python_lint': lambda **kwargs: RiskLevel.SAFE,
            'analyze_complexity': lambda **kwargs: RiskLevel.SAFE,
            'security_scan': lambda **kwargs: RiskLevel.SAFE,
            'analyze_dependencies': lambda **kwargs: RiskLevel.SAFE,
            'code_quality': lambda **kwargs: RiskLevel.SAFE,

            # Code writing operations
            'generate_code': self._assess_code_generation_risk,
            'code_template': lambda **kwargs: RiskLevel.SAFE,
            'refactor_code': self._assess_refactor_risk,
            'code_snippet': lambda **kwargs: RiskLevel.SAFE,

            # Default safe operations
            'read_file': lambda **kwargs: RiskLevel.SAFE,
            'list_files': lambda **kwargs: RiskLevel.SAFE,
            'create_folder': lambda **kwargs: RiskLevel.SAFE,
            'run_python': lambda **kwargs: RiskLevel.LOW,
            'check_syntax': lambda **kwargs: RiskLevel.SAFE,
        }
    
    def requires_approval(self, operation: str, **params) -> bool:
        """Check if operation requires approval"""
        risk_level = self.assess_risk(operation, **params)
        return risk_level != RiskLevel.SAFE
    
    def assess_risk(self, operation: str, **params) -> RiskLevel:
        """Assess risk level of an operation"""
        if operation in self.risk_rules:
            return self.risk_rules[operation](**params)
        return RiskLevel.LOW  # Default to low risk for unknown operations
    
    def request_approval(self, operation: str, **params) -> bool:
        """Request user approval for an operation"""
        risk_level = self.assess_risk(operation, **params)
        
        if risk_level == RiskLevel.SAFE:
            return True
        
        # Create approval request
        request = self._create_approval_request(operation, risk_level, **params)
        
        # Get user approval through CLI
        if self.cli:
            approved = self._get_cli_approval(request)
        else:
            # Fallback to console input
            approved = self._get_console_approval(request)
        
        # Record approval decision
        self.approval_history.append({
            'operation': operation,
            'params': params,
            'risk_level': risk_level.value,
            'approved': approved
        })
        
        return approved
    
    def _assess_file_deletion_risk(self, filepath: str, **kwargs) -> RiskLevel:
        """Assess risk of file deletion"""
        import os
        
        # Check if file exists
        if not os.path.exists(filepath):
            return RiskLevel.SAFE
        
        # Critical system files
        critical_patterns = [
            'main.py', 'requirements.txt', '.env', 'config',
            'database', '.git', 'package.json', 'Cargo.toml'
        ]
        
        filename = os.path.basename(filepath).lower()
        if any(pattern in filename for pattern in critical_patterns):
            return RiskLevel.HIGH
        
        # Check file size
        try:
            size = os.path.getsize(filepath)
            if size > 1024 * 1024:  # > 1MB
                return RiskLevel.MEDIUM
            elif size > 10 * 1024:  # > 10KB
                return RiskLevel.LOW
        except:
            pass
        
        return RiskLevel.LOW
    
    def _assess_folder_deletion_risk(self, folderpath: str, **kwargs) -> RiskLevel:
        """Assess risk of folder deletion"""
        import os
        
        if not os.path.exists(folderpath):
            return RiskLevel.SAFE
        
        # Critical directories
        critical_dirs = [
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            'src', 'lib', 'bin', 'core', 'system'
        ]

        dirname = os.path.basename(folderpath).lower()
        folderpath_lower = folderpath.lower()

        # Check both directory name and full path
        for critical in critical_dirs:
            if critical in dirname or critical in folderpath_lower:
                return RiskLevel.HIGH
        
        # Check if directory has many files
        try:
            item_count = len(os.listdir(folderpath))
            if item_count > 50:
                return RiskLevel.HIGH
            elif item_count > 10:
                return RiskLevel.MEDIUM
            elif item_count > 0:
                return RiskLevel.LOW
        except:
            pass
        
        return RiskLevel.LOW
    
    def _assess_file_write_risk(self, filepath: str, content: str = "", **kwargs) -> RiskLevel:
        """Assess risk of file writing"""
        import os
        
        # Check if overwriting existing file
        if os.path.exists(filepath):
            # Critical files
            critical_patterns = [
                'main.py', 'requirements.txt', '.env', 'config'
            ]
            
            filename = os.path.basename(filepath).lower()
            if any(pattern in filename for pattern in critical_patterns):
                return RiskLevel.MEDIUM
            
            return RiskLevel.LOW
        
        return RiskLevel.SAFE  # New file creation is safe
    
    def _assess_command_risk(self, command: str, **kwargs) -> RiskLevel:
        """Assess risk of shell command execution"""
        command_lower = command.lower()
        
        # Critical commands
        critical_commands = [
            'rm -rf', 'del /f', 'format', 'fdisk', 'mkfs',
            'shutdown', 'reboot', 'halt', 'poweroff',
            'dd if=', 'chmod 777', 'chown root', 'sudo rm'
        ]
        
        for critical in critical_commands:
            if critical in command_lower:
                return RiskLevel.CRITICAL
        
        # High risk commands
        high_risk = [
            'rm ', 'del ', 'rmdir', 'move', 'mv ',
            'chmod', 'chown', 'sudo', 'su ',
            'kill', 'pkill', 'killall'
        ]
        
        for high in high_risk:
            if high in command_lower:
                return RiskLevel.HIGH
        
        # Medium risk commands
        medium_risk = [
            'cp ', 'copy', 'wget', 'curl', 'git push',
            'npm install', 'pip install', 'apt install'
        ]
        
        for medium in medium_risk:
            if medium in command_lower:
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW

    def _assess_git_commit_risk(self, message: str = "", **kwargs) -> RiskLevel:
        """Assess risk of Git commit"""
        if not message:
            return RiskLevel.MEDIUM  # No message is risky

        # Check for potentially problematic commit messages
        risky_patterns = [
            'wip', 'temp', 'test', 'debug', 'hack', 'fix later',
            'todo', 'broken', 'experimental'
        ]

        message_lower = message.lower()
        if any(pattern in message_lower for pattern in risky_patterns):
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _assess_git_push_risk(self, remote: str = "origin", branch: str = "", **kwargs) -> RiskLevel:
        """Assess risk of Git push"""
        # Pushing to main/master branches is higher risk
        if branch.lower() in ['main', 'master', 'production', 'prod']:
            return RiskLevel.HIGH

        # Pushing to origin is generally safe for feature branches
        if remote == "origin" and branch and branch not in ['main', 'master']:
            return RiskLevel.MEDIUM

        return RiskLevel.MEDIUM  # Default medium risk for pushes

    def _assess_git_pull_risk(self, remote: str = "origin", branch: str = "", **kwargs) -> RiskLevel:
        """Assess risk of Git pull"""
        # Pulling is generally safe, but can overwrite local changes
        return RiskLevel.LOW

    def _assess_git_branch_risk(self, action: str = "list", branch_name: str = "", **kwargs) -> RiskLevel:
        """Assess risk of Git branch operations"""
        if action == "list":
            return RiskLevel.SAFE
        elif action == "create":
            return RiskLevel.LOW
        elif action == "switch":
            return RiskLevel.LOW
        elif action == "delete":
            # Deleting main/master is high risk
            if branch_name.lower() in ['main', 'master', 'production', 'prod']:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _create_approval_request(self, operation: str, risk_level: RiskLevel, **params) -> ApprovalRequest:
        """Create an approval request with details"""
        
        # Generate operation description
        descriptions = {
            'delete_file': f"Delete file: {params.get('filepath', 'unknown')}",
            'delete_folder': f"Delete folder: {params.get('folderpath', 'unknown')}",
            'write_file': f"Write to file: {params.get('filepath', 'unknown')}",
            'run_command': f"Execute command: {params.get('command', 'unknown')}",
            'git_commit': f"Commit changes: {params.get('message', 'no message')}",
            'git_push': f"Push to {params.get('remote', 'origin')}/{params.get('branch', 'current branch')}",
            'git_pull': f"Pull from {params.get('remote', 'origin')}/{params.get('branch', 'current branch')}",
            'git_branch': f"Branch {params.get('action', 'operation')}: {params.get('branch_name', '')}",
            'git_add': f"Stage files: {params.get('filepath', '.')}",
        }
        
        description = descriptions.get(operation, f"Execute {operation}")
        
        # Generate warnings based on risk level
        warnings = []
        if risk_level == RiskLevel.HIGH:
            warnings.append("⚠️  This operation affects important files/directories")
            warnings.append("⚠️  This action cannot be easily undone")
        elif risk_level == RiskLevel.CRITICAL:
            warnings.append("🚨 CRITICAL: This command is potentially destructive")
            warnings.append("🚨 This could damage your system or data")
            warnings.append("🚨 Proceed only if you are absolutely certain")
        
        return ApprovalRequest(
            operation=operation,
            description=description,
            risk_level=risk_level,
            details=params,
            warnings=warnings
        )
    
    def _get_cli_approval(self, request: ApprovalRequest) -> bool:
        """Get approval through CLI interface"""
        return self.cli.ask_approval(
            message=request.description,
            risk_level=request.risk_level,
            warnings=request.warnings,
            details=request.details
        )
    
    def _get_console_approval(self, request: ApprovalRequest) -> bool:
        """Fallback console approval"""
        print(f"\n⚠️  APPROVAL REQUIRED: {request.description}")
        
        if request.warnings:
            for warning in request.warnings:
                print(warning)
        
        if request.risk_level == RiskLevel.CRITICAL:
            print("\nType 'I UNDERSTAND THE RISKS' to proceed:")
            response = input().strip()
            return response == "I UNDERSTAND THE RISKS"
        else:
            response = input("\nProceed? (y/N): ").strip().lower()
            return response in ['y', 'yes']

    def _assess_code_generation_risk(self, **kwargs) -> RiskLevel:
        """Assess risk for code generation operations"""
        filepath = kwargs.get('filepath', '')
        description = kwargs.get('description', '').lower()

        # Higher risk if writing to important files
        if filepath:
            if any(important in filepath.lower() for important in
                   ['main.py', '__init__.py', 'setup.py', 'config']):
                return RiskLevel.MEDIUM

        # Higher risk for system-level operations
        if any(risky in description for risky in
               ['system', 'os.', 'subprocess', 'exec', 'eval']):
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _assess_refactor_risk(self, **kwargs) -> RiskLevel:
        """Assess risk for code refactoring operations"""
        filepath = kwargs.get('filepath', '')
        refactor_type = kwargs.get('refactor_type', '')

        # Higher risk for important files
        if any(important in filepath.lower() for important in
               ['main.py', '__init__.py', 'setup.py']):
            return RiskLevel.HIGH

        # Auto refactoring is riskier than specific operations
        if refactor_type == 'auto':
            return RiskLevel.MEDIUM

        return RiskLevel.LOW
