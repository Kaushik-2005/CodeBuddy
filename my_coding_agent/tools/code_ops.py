"""
Code Execution Tools - Safe code and command execution
"""
import os
import subprocess
import sys
from typing import Dict, List
from .base_tool import BaseTool, ToolResult


class RunPythonTool(BaseTool):
    """Tool for executing Python files"""
    
    def __init__(self):
        super().__init__(
            name="run_python",
            description="Execute a Python file and capture output"
        )
    
    def execute(self, filepath: str, **kwargs) -> ToolResult:
        """Run a Python file"""
        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    message=f"❌ Python file not found: {filepath}"
                )
            
            if not filepath.endswith('.py'):
                return ToolResult(
                    success=False,
                    message=f"❌ Not a Python file: {filepath}"
                )
            
            # Execute the Python file
            result = subprocess.run(
                [sys.executable, filepath],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=os.path.dirname(os.path.abspath(filepath)) or "."
            )
            
            output = ""
            if result.stdout:
                output += f"📤 **Output:**\n{result.stdout}\n"
            
            if result.stderr:
                output += f"⚠️ **Errors:**\n{result.stderr}\n"
            
            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    message=f"✅ Executed {filepath}\n{output}",
                    data={
                        "filepath": filepath,
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    message=f"❌ Execution failed (exit code: {result.returncode})\n{output}",
                    data={
                        "filepath": filepath,
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                )
                
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                message=f"❌ Execution timeout: {filepath} (>30 seconds)"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error executing Python file: {e}"
            )
    
    def get_parameters(self) -> Dict[str, str]:
        return {"filepath": "Path to the Python file to execute"}


class RunCommandTool(BaseTool):
    """Tool for executing shell commands (requires approval)"""
    
    def __init__(self):
        super().__init__(
            name="run_command",
            description="Execute a shell command (requires approval)"
        )
    
    def execute(self, command: str, **kwargs) -> ToolResult:
        """Execute a shell command"""
        try:
            # Safety check - block dangerous commands
            dangerous_commands = [
                'rm -rf', 'del /f', 'format', 'fdisk', 'mkfs',
                'shutdown', 'reboot', 'halt', 'poweroff',
                'dd if=', 'chmod 777', 'chown root'
            ]
            
            command_lower = command.lower()
            for dangerous in dangerous_commands:
                if dangerous in command_lower:
                    return ToolResult(
                        success=False,
                        message=f"❌ Dangerous command blocked: {command}"
                    )
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=os.getcwd()
            )
            
            output = ""
            if result.stdout:
                output += f"📤 **Output:**\n{result.stdout}\n"
            
            if result.stderr:
                output += f"⚠️ **Errors:**\n{result.stderr}\n"
            
            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    message=f"✅ Command executed: `{command}`\n{output}",
                    data={
                        "command": command,
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    },
                    requires_approval=True  # Shell commands require approval
                )
            else:
                return ToolResult(
                    success=False,
                    message=f"❌ Command failed (exit code: {result.returncode})\n{output}",
                    data={
                        "command": command,
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    },
                    requires_approval=True
                )
                
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                message=f"❌ Command timeout: {command} (>30 seconds)"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error executing command: {e}"
            )
    
    def get_parameters(self) -> Dict[str, str]:
        return {"command": "Shell command to execute"}


class CheckSyntaxTool(BaseTool):
    """Tool for checking Python syntax"""
    
    def __init__(self):
        super().__init__(
            name="check_syntax",
            description="Check Python file syntax for errors"
        )
    
    def execute(self, filepath: str, **kwargs) -> ToolResult:
        """Check Python file syntax"""
        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    message=f"❌ File not found: {filepath}"
                )
            
            if not filepath.endswith('.py'):
                return ToolResult(
                    success=False,
                    message=f"❌ Not a Python file: {filepath}"
                )
            
            # Read and compile the file
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            try:
                compile(source_code, filepath, 'exec')
                return ToolResult(
                    success=True,
                    message=f"✅ Syntax check passed: {filepath}",
                    data={"filepath": filepath, "lines": len(source_code.split('\n'))}
                )
            except SyntaxError as e:
                return ToolResult(
                    success=False,
                    message=f"❌ Syntax error in {filepath}:\nLine {e.lineno}: {e.msg}\n{e.text}",
                    data={
                        "filepath": filepath,
                        "error": str(e),
                        "line": e.lineno,
                        "text": e.text
                    }
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error checking syntax: {e}"
            )
    
    def get_parameters(self) -> Dict[str, str]:
        return {"filepath": "Path to the Python file to check"}


# Tool factory functions for easy registration
def create_code_tools() -> List[BaseTool]:
    """Create all code execution tools"""
    return [
        RunPythonTool(),
        RunCommandTool(),
        CheckSyntaxTool()
    ]
