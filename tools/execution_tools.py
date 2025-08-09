import subprocess
import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict

def run_python(filepath: str, args: List[str] = None, timeout: int = 30) -> str:
    """Execute a Python script safely with output capture"""
    try:
        if not os.path.exists(filepath):
            return f"❌ Python file not found: {filepath}"
        
        if not filepath.endswith('.py'):
            return f"❌ File must be a Python file (.py): {filepath}"
        
        # Build command
        cmd = [sys.executable, filepath]
        if args:
            cmd.extend(args)
        
        start_time = time.time()
        
        # Execute with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(filepath) if os.path.dirname(filepath) else "."
        )
        
        execution_time = time.time() - start_time
        
        # Format output
        output = f"🐍 Executed Python script: {filepath}\n"
        output += f"⏱️ Execution time: {execution_time:.2f}s\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 STDOUT:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ STDERR:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += "✅ Script executed successfully"
        else:
            output += f"❌ Script failed with exit code {result.returncode}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Python script timed out after {timeout} seconds"
    except Exception as e:
        return f"❌ Error executing Python script: {e}"

def run_tests(test_path: str = ".", framework: str = "auto", timeout: int = 60) -> str:
    """Run test suites using various testing frameworks"""
    try:
        if not os.path.exists(test_path):
            return f"❌ Test path not found: {test_path}"
        
        # Auto-detect framework if not specified
        if framework == "auto":
            if _has_pytest_files(test_path):
                framework = "pytest"
            elif _has_unittest_files(test_path):
                framework = "unittest"
            elif _has_jest_files(test_path):
                framework = "jest"
            else:
                return f"❌ No supported test framework detected in {test_path}"
        
        if framework == "pytest":
            return _run_pytest(test_path, timeout)
        elif framework == "unittest":
            return _run_unittest(test_path, timeout)
        elif framework == "jest":
            return _run_jest(test_path, timeout)
        else:
            return f"❌ Unsupported test framework: {framework}"
    
    except Exception as e:
        return f"❌ Error running tests: {e}"

def _has_pytest_files(path: str) -> bool:
    """Check if directory contains pytest files"""
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                return True
            if file.endswith('_test.py'):
                return True
    return False

def _has_unittest_files(path: str) -> bool:
    """Check if directory contains unittest files"""
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'import unittest' in content or 'from unittest' in content:
                            return True
                except:
                    continue
    return False

def _has_jest_files(path: str) -> bool:
    """Check if directory contains Jest test files"""
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.test.js') or file.endswith('.spec.js'):
                return True
    return False

def _run_pytest(test_path: str, timeout: int) -> str:
    """Run pytest tests"""
    try:
        cmd = ["pytest", test_path, "-v", "--tb=short"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"🧪 Pytest Results for {test_path}\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Test Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ Errors:\n{result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Pytest timed out after {timeout} seconds"
    except FileNotFoundError:
        return "❌ Pytest not installed. Install with: pip install pytest"
    except Exception as e:
        return f"❌ Error running pytest: {e}"

def _run_unittest(test_path: str, timeout: int) -> str:
    """Run unittest tests"""
    try:
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", test_path, "-v"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"🧪 Unittest Results for {test_path}\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Test Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ Errors:\n{result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Unittest timed out after {timeout} seconds"
    except Exception as e:
        return f"❌ Error running unittest: {e}"

def _run_jest(test_path: str, timeout: int) -> str:
    """Run Jest tests"""
    try:
        cmd = ["npm", "test"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=test_path
        )
        
        output = f"🧪 Jest Results for {test_path}\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Test Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ Errors:\n{result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Jest timed out after {timeout} seconds"
    except FileNotFoundError:
        return "❌ Node.js/npm not found. Please install Node.js"
    except Exception as e:
        return f"❌ Error running Jest: {e}"

def run_command(command: str, working_dir: str = ".", timeout: int = 30, safe_mode: bool = True) -> str:
    """Execute shell commands safely with restrictions"""
    try:
        # Safety checks for dangerous commands
        if safe_mode:
            dangerous_commands = [
                'rm', 'del', 'format', 'fdisk', 'mkfs', 'shutdown', 'reboot',
                'sudo rm', 'rm -rf', 'rmdir /s', 'format c:', '>>', 'dd if='
            ]
            
            cmd_lower = command.lower()
            for dangerous in dangerous_commands:
                if dangerous in cmd_lower:
                    return f"❌ Dangerous command blocked: {command}\nUse safe_mode=False to override (not recommended)"
        
        # Expand working directory
        expanded_dir = os.path.expandvars(os.path.expanduser(working_dir))
        if not os.path.exists(expanded_dir):
            return f"❌ Working directory not found: {expanded_dir}"
        
        start_time = time.time()
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=expanded_dir
        )
        
        execution_time = time.time() - start_time
        
        # Format output
        output = f"💻 Executed command: {command}\n"
        output += f"📂 Working directory: {expanded_dir}\n"
        output += f"⏱️ Execution time: {execution_time:.2f}s\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 STDOUT:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ STDERR:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += "✅ Command executed successfully"
        else:
            output += f"❌ Command failed with exit code {result.returncode}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Command timed out after {timeout} seconds"
    except Exception as e:
        return f"❌ Error executing command: {e}"

def install_package(package_name: str, package_manager: str = "auto", upgrade: bool = False) -> str:
    """Install packages using various package managers"""
    try:
        # Auto-detect package manager
        if package_manager == "auto":
            if _is_python_project():
                package_manager = "pip"
            elif _is_node_project():
                package_manager = "npm"
            else:
                return "❌ Could not auto-detect package manager. Please specify: pip, npm, yarn"
        
        if package_manager == "pip":
            return _install_pip_package(package_name, upgrade)
        elif package_manager == "npm":
            return _install_npm_package(package_name)
        elif package_manager == "yarn":
            return _install_yarn_package(package_name)
        else:
            return f"❌ Unsupported package manager: {package_manager}"
    
    except Exception as e:
        return f"❌ Error installing package: {e}"

def _is_python_project() -> bool:
    """Check if current directory is a Python project"""
    python_indicators = ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile']
    return any(os.path.exists(indicator) for indicator in python_indicators)

def _is_node_project() -> bool:
    """Check if current directory is a Node.js project"""
    return os.path.exists('package.json')

def _install_pip_package(package_name: str, upgrade: bool) -> str:
    """Install Python package with pip"""
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        cmd.append(package_name)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # Longer timeout for package installation
        )
        
        output = f"📦 Pip install: {package_name}\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ Errors:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += f"✅ Successfully installed {package_name}"
        else:
            output += f"❌ Failed to install {package_name}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Package installation timed out"
    except Exception as e:
        return f"❌ Error installing pip package: {e}"

def _install_npm_package(package_name: str) -> str:
    """Install Node.js package with npm"""
    try:
        cmd = ["npm", "install", package_name]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = f"📦 NPM install: {package_name}\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ Errors:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += f"✅ Successfully installed {package_name}"
        else:
            output += f"❌ Failed to install {package_name}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Package installation timed out"
    except FileNotFoundError:
        return "❌ npm not found. Please install Node.js"
    except Exception as e:
        return f"❌ Error installing npm package: {e}"

def _install_yarn_package(package_name: str) -> str:
    """Install Node.js package with Yarn"""
    try:
        cmd = ["yarn", "add", package_name]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = f"📦 Yarn add: {package_name}\n"
        output += f"🔢 Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"📤 Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"❌ Errors:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += f"✅ Successfully installed {package_name}"
        else:
            output += f"❌ Failed to install {package_name}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"⏰ Package installation timed out"
    except FileNotFoundError:
        return "❌ Yarn not found. Please install Yarn"
    except Exception as e:
        return f"❌ Error installing yarn package: {e}"

def check_environment() -> str:
    """Check development environment and available tools"""
    try:
        env_info = "🔧 Development Environment Check\n"
        env_info += "=" * 40 + "\n\n"
        
        # Python information
        env_info += f"🐍 Python: {sys.version.split()[0]} ({sys.executable})\n"
        
        # Check common tools
        tools_to_check = [
            ("pip", [sys.executable, "-m", "pip", "--version"]),
            ("pytest", ["pytest", "--version"]),
            ("pylint", ["pylint", "--version"]),
            ("flake8", ["flake8", "--version"]),
            ("node", ["node", "--version"]),
            ("npm", ["npm", "--version"]),
            ("git", ["git", "--version"])
        ]
        
        env_info += "\n📋 Available Tools:\n"
        for tool_name, cmd in tools_to_check:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    env_info += f"  ✅ {tool_name}: {version}\n"
                else:
                    env_info += f"  ❌ {tool_name}: Not working\n"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                env_info += f"  ❌ {tool_name}: Not installed\n"
            except Exception:
                env_info += f"  ⚠️ {tool_name}: Error checking\n"
        
        # Project type detection
        env_info += "\n📂 Project Type Detection:\n"
        if _is_python_project():
            env_info += "  🐍 Python project detected\n"
        if _is_node_project():
            env_info += "  🌐 Node.js project detected\n"
        if os.path.exists('.git'):
            env_info += "  📝 Git repository\n"
        
        return env_info
        
    except Exception as e:
        return f"❌ Error checking environment: {e}"