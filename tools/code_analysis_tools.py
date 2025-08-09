import subprocess
import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional

def validate_syntax(filepath: str) -> str:
    """Validate syntax of code files"""
    try:
        if not os.path.exists(filepath):
            return f"❌ File {filepath} does not exist"
        
        file_ext = Path(filepath).suffix.lower()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file_ext == '.py':
            return _validate_python_syntax(content, filepath)
        elif file_ext in ['.js', '.ts']:
            return _validate_javascript_syntax(content, filepath)
        elif file_ext in ['.java']:
            return _validate_java_syntax(content, filepath)
        else:
            return f"⚠️ Syntax validation not supported for {file_ext} files"
    
    except Exception as e:
        return f"❌ Error validating syntax: {e}"

def _validate_python_syntax(content: str, filepath: str) -> str:
    """Validate Python syntax using AST"""
    try:
        ast.parse(content)
        return f"✅ Python syntax is valid in {filepath}"
    except SyntaxError as e:
        return f"❌ Python syntax error in {filepath}:\n  Line {e.lineno}: {e.msg}\n  {e.text.strip() if e.text else ''}"
    except Exception as e:
        return f"❌ Error parsing Python file: {e}"

def _validate_javascript_syntax(content: str, filepath: str) -> str:
    """Basic JavaScript syntax validation"""
    try:
        # Check for basic syntax issues
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            # Check for unmatched brackets/braces
            open_chars = '([{'
            close_chars = ')]}'
            stack = []
            
            for char in line:
                if char in open_chars:
                    stack.append(char)
                elif char in close_chars:
                    if not stack:
                        issues.append(f"Line {i}: Unmatched closing '{char}'")
                    else:
                        expected = close_chars[open_chars.index(stack.pop())]
                        if char != expected:
                            issues.append(f"Line {i}: Expected '{expected}' but found '{char}'")
        
        if issues:
            return f"⚠️ Potential JavaScript syntax issues in {filepath}:\n" + "\n".join(issues)
        else:
            return f"✅ Basic JavaScript syntax check passed for {filepath}"
            
    except Exception as e:
        return f"❌ Error checking JavaScript syntax: {e}"

def _validate_java_syntax(content: str, filepath: str) -> str:
    """Basic Java syntax validation"""
    try:
        # Check for basic Java structure
        if 'class ' not in content:
            return f"⚠️ No class definition found in Java file {filepath}"
        
        # Check for unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            return f"❌ Unmatched braces in {filepath}: {open_braces} open, {close_braces} close"
        
        return f"✅ Basic Java syntax check passed for {filepath}"
        
    except Exception as e:
        return f"❌ Error checking Java syntax: {e}"

def run_linter(filepath: str, linter_type: str = "auto") -> str:
    """Run code linter on file"""
    try:
        if not os.path.exists(filepath):
            return f"❌ File {filepath} does not exist"
        
        file_ext = Path(filepath).suffix.lower()
        
        if linter_type == "auto":
            if file_ext == '.py':
                linter_type = "pylint"
            elif file_ext in ['.js', '.ts']:
                linter_type = "eslint"
            else:
                return f"⚠️ No default linter for {file_ext} files"
        
        if linter_type == "pylint":
            return _run_pylint(filepath)
        elif linter_type == "flake8":
            return _run_flake8(filepath)
        elif linter_type == "eslint":
            return _run_eslint(filepath)
        else:
            return f"❌ Unknown linter type: {linter_type}"
    
    except Exception as e:
        return f"❌ Error running linter: {e}"

def _run_pylint(filepath: str) -> str:
    """Run pylint on Python file"""
    try:
        result = subprocess.run(
            ["pylint", "--output-format=text", "--score=no", filepath],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return f"✅ Pylint found no issues in {filepath}"
        else:
            output = result.stdout if result.stdout else result.stderr
            return f"⚠️ Pylint analysis for {filepath}:\n{output}"
            
    except subprocess.TimeoutExpired:
        return f"⏰ Pylint timed out for {filepath}"
    except FileNotFoundError:
        return f"⚠️ Pylint not installed. Install with: pip install pylint"
    except Exception as e:
        return f"❌ Error running pylint: {e}"

def _run_flake8(filepath: str) -> str:
    """Run flake8 on Python file"""
    try:
        result = subprocess.run(
            ["flake8", filepath],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return f"✅ Flake8 found no issues in {filepath}"
        else:
            return f"⚠️ Flake8 analysis for {filepath}:\n{result.stdout}"
            
    except subprocess.TimeoutExpired:
        return f"⏰ Flake8 timed out for {filepath}"
    except FileNotFoundError:
        return f"⚠️ Flake8 not installed. Install with: pip install flake8"
    except Exception as e:
        return f"❌ Error running flake8: {e}"

def _run_eslint(filepath: str) -> str:
    """Run ESLint on JavaScript/TypeScript file"""
    try:
        result = subprocess.run(
            ["eslint", filepath],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return f"✅ ESLint found no issues in {filepath}"
        else:
            return f"⚠️ ESLint analysis for {filepath}:\n{result.stdout}"
            
    except subprocess.TimeoutExpired:
        return f"⏰ ESLint timed out for {filepath}"
    except FileNotFoundError:
        return f"⚠️ ESLint not installed. Install with: npm install -g eslint"
    except Exception as e:
        return f"❌ Error running ESLint: {e}"

def find_references(symbol: str, directory: str = ".", file_extensions: List[str] = None) -> str:
    """Find all references to a symbol (function, class, variable) in codebase"""
    try:
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c']
        
        references = []
        
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            
                        for line_num, line in enumerate(lines, 1):
                            if symbol in line:
                                # Check if it's a whole word match
                                if re.search(r'\b' + re.escape(symbol) + r'\b', line):
                                    references.append({
                                        'file': filepath,
                                        'line': line_num,
                                        'content': line.strip()
                                    })
                    except:
                        continue
        
        if references:
            result = f"Found {len(references)} references to '{symbol}':\n\n"
            for ref in references[:20]:  # Limit to first 20 results
                result += f"📁 {ref['file']}:{ref['line']}\n"
                result += f"   {ref['content']}\n\n"
            
            if len(references) > 20:
                result += f"... and {len(references) - 20} more references"
            
            return result
        else:
            return f"No references found for '{symbol}'"
    
    except Exception as e:
        return f"❌ Error finding references: {e}"

def analyze_complexity(filepath: str) -> str:
    """Analyze code complexity metrics"""
    try:
        if not os.path.exists(filepath):
            return f"❌ File {filepath} does not exist"
        
        file_ext = Path(filepath).suffix.lower()
        
        if file_ext == '.py':
            return _analyze_python_complexity(filepath)
        else:
            return f"⚠️ Complexity analysis not supported for {file_ext} files yet"
    
    except Exception as e:
        return f"❌ Error analyzing complexity: {e}"

def _analyze_python_complexity(filepath: str) -> str:
    """Analyze Python code complexity"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        stats = {
            'functions': 0,
            'classes': 0,
            'lines': len(content.split('\n')),
            'complexity_score': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                stats['functions'] += 1
                stats['complexity_score'] += _calculate_cyclomatic_complexity(node)
            elif isinstance(node, ast.ClassDef):
                stats['classes'] += 1
        
        result = f"📊 Complexity Analysis for {filepath}:\n"
        result += f"  📝 Lines of code: {stats['lines']}\n"
        result += f"  🔧 Functions: {stats['functions']}\n"
        result += f"  🏗️  Classes: {stats['classes']}\n"
        result += f"  🧮 Complexity score: {stats['complexity_score']}\n"
        
        if stats['complexity_score'] > 20:
            result += f"  ⚠️  High complexity - consider refactoring"
        elif stats['complexity_score'] > 10:
            result += f"  💡 Moderate complexity"
        else:
            result += f"  ✅ Low complexity - good!"
        
        return result
    
    except Exception as e:
        return f"❌ Error analyzing Python complexity: {e}"

def _calculate_cyclomatic_complexity(node) -> int:
    """Calculate cyclomatic complexity for a function"""
    complexity = 1  # Base complexity
    
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                            ast.ExceptHandler, ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    
    return complexity

def code_quality_report(directory: str = ".") -> str:
    """Generate a comprehensive code quality report"""
    try:
        python_files = []
        js_files = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith('.py'):
                    python_files.append(filepath)
                elif file.endswith(('.js', '.ts')):
                    js_files.append(filepath)
        
        report = f"📋 Code Quality Report for {directory}\n"
        report += f"=" * 50 + "\n\n"
        
        # Python files analysis
        if python_files:
            report += f"🐍 Python Files ({len(python_files)} files):\n"
            syntax_issues = 0
            
            for file in python_files[:5]:  # Analyze first 5 files
                syntax_result = validate_syntax(file)
                if "❌" in syntax_result:
                    syntax_issues += 1
                    report += f"  {syntax_result}\n"
            
            report += f"  Syntax Issues: {syntax_issues}/{min(len(python_files), 5)}\n\n"
        
        # JavaScript files analysis
        if js_files:
            report += f"🌐 JavaScript/TypeScript Files ({len(js_files)} files):\n"
            for file in js_files[:3]:  # Analyze first 3 files
                syntax_result = validate_syntax(file)
                report += f"  {os.path.basename(file)}: {'✅' if '✅' in syntax_result else '⚠️'}\n"
            report += "\n"
        
        # Overall stats
        total_files = len(python_files) + len(js_files)
        report += f"📊 Summary:\n"
        report += f"  Total analyzed files: {total_files}\n"
        report += f"  Python files: {len(python_files)}\n"
        report += f"  JS/TS files: {len(js_files)}\n"
        
        return report
    
    except Exception as e:
        return f"❌ Error generating quality report: {e}"