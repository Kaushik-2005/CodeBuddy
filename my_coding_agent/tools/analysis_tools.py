"""
Code Analysis Tools - Linting, complexity, security, and quality analysis
"""
import ast
import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnalysisResult:
    """Result of code analysis"""
    tool: str
    file_path: str
    issues: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    score: Optional[float] = None
    summary: str = ""


class PythonLinterTool:
    """Python code linting using built-in AST and pattern matching"""
    
    def execute(self, filepath: str, directory: str = ".") -> str:
        """Lint Python code"""
        try:
            full_path = os.path.join(directory, filepath)
            
            if not os.path.exists(full_path):
                return f"❌ File not found: {filepath}"
            
            if not filepath.endswith('.py'):
                return f"❌ Not a Python file: {filepath}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # Syntax check using AST
            try:
                tree = ast.parse(content)
                issues.extend(self._analyze_ast(tree, content))
            except SyntaxError as e:
                issues.append({
                    'type': 'syntax_error',
                    'line': e.lineno,
                    'message': str(e),
                    'severity': 'error'
                })
            
            # Pattern-based checks
            issues.extend(self._pattern_checks(content))
            
            return self._format_lint_results(filepath, issues)
            
        except Exception as e:
            return f"❌ Linting failed: {e}"
    
    def _analyze_ast(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Analyze AST for code issues"""
        issues = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            # Check for unused variables (simplified)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if node.id.startswith('_') and len(node.id) > 1:
                    issues.append({
                        'type': 'style',
                        'line': node.lineno,
                        'message': f"Variable '{node.id}' starts with underscore (private convention)",
                        'severity': 'info'
                    })
            
            # Check for long functions
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        issues.append({
                            'type': 'complexity',
                            'line': node.lineno,
                            'message': f"Function '{node.name}' is {func_length} lines long (consider breaking it down)",
                            'severity': 'warning'
                        })
            
            # Check for too many arguments
            if isinstance(node, ast.FunctionDef):
                arg_count = len(node.args.args)
                if arg_count > 5:
                    issues.append({
                        'type': 'complexity',
                        'line': node.lineno,
                        'message': f"Function '{node.name}' has {arg_count} arguments (consider using fewer)",
                        'severity': 'warning'
                    })
            
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append({
                        'type': 'best_practice',
                        'line': node.lineno,
                        'message': "Bare 'except:' clause (specify exception type)",
                        'severity': 'warning'
                    })
        
        return issues
    
    def _pattern_checks(self, content: str) -> List[Dict[str, Any]]:
        """Pattern-based code checks"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 100:
                issues.append({
                    'type': 'style',
                    'line': i,
                    'message': f"Line too long ({len(line)} characters, max 100)",
                    'severity': 'info'
                })
            
            # Check for TODO/FIXME comments
            if re.search(r'#.*\b(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
                issues.append({
                    'type': 'maintenance',
                    'line': i,
                    'message': "TODO/FIXME comment found",
                    'severity': 'info'
                })
            
            # Check for print statements (potential debug code)
            if re.search(r'\bprint\s*\(', line) and 'def ' not in line:
                issues.append({
                    'type': 'debug',
                    'line': i,
                    'message': "Print statement found (consider using logging)",
                    'severity': 'info'
                })
            
            # Check for hardcoded passwords/secrets
            if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                issues.append({
                    'type': 'security',
                    'line': i,
                    'message': "Potential hardcoded secret detected",
                    'severity': 'error'
                })
        
        return issues
    
    def _format_lint_results(self, filepath: str, issues: List[Dict[str, Any]]) -> str:
        """Format linting results for display"""
        if not issues:
            return f"✅ **{filepath}**: No issues found! Clean code! 🎉"
        
        lines = [f"📋 **Linting Results for {filepath}:**\n"]
        
        # Group by severity
        errors = [i for i in issues if i['severity'] == 'error']
        warnings = [i for i in issues if i['severity'] == 'warning']
        info = [i for i in issues if i['severity'] == 'info']
        
        if errors:
            lines.append("🔴 **Errors:**")
            for issue in errors:
                lines.append(f"  • Line {issue['line']}: {issue['message']}")
            lines.append("")
        
        if warnings:
            lines.append("🟡 **Warnings:**")
            for issue in warnings:
                lines.append(f"  • Line {issue['line']}: {issue['message']}")
            lines.append("")
        
        if info:
            lines.append("🔵 **Info:**")
            for issue in info:
                lines.append(f"  • Line {issue['line']}: {issue['message']}")
            lines.append("")
        
        # Summary
        total = len(issues)
        lines.append(f"📊 **Summary**: {len(errors)} errors, {len(warnings)} warnings, {len(info)} info ({total} total)")
        
        return '\n'.join(lines)


class ComplexityAnalyzerTool:
    """Analyze code complexity metrics"""
    
    def execute(self, filepath: str, directory: str = ".") -> str:
        """Analyze code complexity"""
        try:
            full_path = os.path.join(directory, filepath)
            
            if not os.path.exists(full_path):
                return f"❌ File not found: {filepath}"
            
            if not filepath.endswith('.py'):
                return f"❌ Not a Python file: {filepath}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                metrics = self._calculate_metrics(tree, content)
                return self._format_complexity_results(filepath, metrics)
            except SyntaxError as e:
                return f"❌ Syntax error in {filepath}: {e}"
            
        except Exception as e:
            return f"❌ Complexity analysis failed: {e}"
    
    def _calculate_metrics(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Calculate various complexity metrics"""
        lines = content.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'functions': 0,
            'classes': 0,
            'max_function_length': 0,
            'avg_function_length': 0,
            'cyclomatic_complexity': 0,
            'function_details': []
        }
        
        function_lengths = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['functions'] += 1
                
                # Calculate function length
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    function_lengths.append(func_length)
                    metrics['max_function_length'] = max(metrics['max_function_length'], func_length)
                    
                    # Calculate cyclomatic complexity for this function
                    complexity = self._calculate_cyclomatic_complexity(node)
                    
                    metrics['function_details'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'length': func_length,
                        'complexity': complexity,
                        'args': len(node.args.args)
                    })
            
            elif isinstance(node, ast.ClassDef):
                metrics['classes'] += 1
        
        if function_lengths:
            metrics['avg_function_length'] = sum(function_lengths) / len(function_lengths)
        
        # Overall cyclomatic complexity
        metrics['cyclomatic_complexity'] = self._calculate_cyclomatic_complexity(tree)
        
        return metrics
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # And/Or operations
                complexity += len(child.values) - 1
        
        return complexity
    
    def _format_complexity_results(self, filepath: str, metrics: Dict[str, Any]) -> str:
        """Format complexity analysis results"""
        lines = [f"📊 **Complexity Analysis for {filepath}:**\n"]
        
        # Overall metrics
        lines.append("📈 **Overall Metrics:**")
        lines.append(f"  • Total lines: {metrics['total_lines']}")
        lines.append(f"  • Code lines: {metrics['code_lines']}")
        lines.append(f"  • Comment lines: {metrics['comment_lines']}")
        lines.append(f"  • Blank lines: {metrics['blank_lines']}")
        lines.append(f"  • Functions: {metrics['functions']}")
        lines.append(f"  • Classes: {metrics['classes']}")
        lines.append(f"  • Cyclomatic complexity: {metrics['cyclomatic_complexity']}")
        lines.append("")
        
        # Function metrics
        if metrics['functions'] > 0:
            lines.append("🔧 **Function Metrics:**")
            lines.append(f"  • Average function length: {metrics['avg_function_length']:.1f} lines")
            lines.append(f"  • Longest function: {metrics['max_function_length']} lines")
            lines.append("")
            
            # Function details
            if metrics['function_details']:
                lines.append("📋 **Function Details:**")
                for func in metrics['function_details']:
                    complexity_emoji = "🟢" if func['complexity'] <= 5 else "🟡" if func['complexity'] <= 10 else "🔴"
                    lines.append(f"  • {func['name']} (line {func['line']}): {func['length']} lines, complexity {func['complexity']} {complexity_emoji}")
                lines.append("")
        
        # Quality assessment
        lines.append("🎯 **Quality Assessment:**")
        
        # Code quality score (simplified)
        score = 100
        if metrics['cyclomatic_complexity'] > 20:
            score -= 20
        if metrics['max_function_length'] > 50:
            score -= 15
        if metrics['avg_function_length'] > 30:
            score -= 10
        
        score_emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        lines.append(f"  • Quality Score: {score}/100 {score_emoji}")
        
        if score < 80:
            lines.append("  • Suggestions:")
            if metrics['cyclomatic_complexity'] > 20:
                lines.append("    - Consider breaking down complex logic")
            if metrics['max_function_length'] > 50:
                lines.append("    - Break down long functions")
            if metrics['avg_function_length'] > 30:
                lines.append("    - Functions are generally too long")
        
        return '\n'.join(lines)


class SecurityScannerTool:
    """Security vulnerability scanner for Python code"""

    def execute(self, filepath: str, directory: str = ".") -> str:
        """Scan for security vulnerabilities"""
        try:
            full_path = os.path.join(directory, filepath)

            if not os.path.exists(full_path):
                return f"❌ File not found: {filepath}"

            if not filepath.endswith('.py'):
                return f"❌ Not a Python file: {filepath}"

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            vulnerabilities = []

            # Pattern-based security checks
            vulnerabilities.extend(self._check_security_patterns(content))

            # AST-based security checks
            try:
                tree = ast.parse(content)
                vulnerabilities.extend(self._check_ast_security(tree))
            except SyntaxError:
                pass  # Already handled in linter

            return self._format_security_results(filepath, vulnerabilities)

        except Exception as e:
            return f"❌ Security scan failed: {e}"

    def _check_security_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Check for security patterns in code"""
        vulnerabilities = []
        lines = content.split('\n')

        security_patterns = [
            # SQL Injection risks
            (r'execute\s*\(\s*["\'].*%.*["\']', 'sql_injection', 'Potential SQL injection vulnerability'),
            (r'cursor\.execute\s*\(\s*.*\+.*\)', 'sql_injection', 'SQL query concatenation detected'),

            # Command injection
            (r'os\.system\s*\(.*\+', 'command_injection', 'Command injection risk with string concatenation'),
            (r'subprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True', 'command_injection', 'Shell=True with subprocess is risky'),

            # Hardcoded secrets
            (r'(password|secret|key|token|api_key)\s*=\s*["\'][^"\']{8,}["\']', 'hardcoded_secret', 'Hardcoded secret detected'),
            (r'["\'][A-Za-z0-9+/]{20,}={0,2}["\']', 'potential_secret', 'Potential base64 encoded secret'),

            # Insecure random
            (r'import\s+random\b', 'weak_random', 'Using random module for security purposes is not cryptographically secure'),

            # Pickle security
            (r'pickle\.loads?\s*\(', 'pickle_security', 'Pickle deserialization can execute arbitrary code'),

            # Eval/exec usage
            (r'\beval\s*\(', 'code_injection', 'eval() can execute arbitrary code'),
            (r'\bexec\s*\(', 'code_injection', 'exec() can execute arbitrary code'),

            # Insecure HTTP
            (r'http://[^"\'\s]+', 'insecure_http', 'Insecure HTTP URL detected'),

            # Debug mode
            (r'debug\s*=\s*True', 'debug_mode', 'Debug mode enabled in production code'),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, vuln_type, message in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    severity = 'high' if vuln_type in ['sql_injection', 'command_injection', 'code_injection'] else 'medium'
                    vulnerabilities.append({
                        'type': vuln_type,
                        'line': i,
                        'message': message,
                        'severity': severity,
                        'code': line.strip()
                    })

        return vulnerabilities

    def _check_ast_security(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """AST-based security checks"""
        from .security_tools import check_ast_security
        return check_ast_security(tree)

    def _format_security_results(self, filepath: str, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Format security scan results"""
        from .security_tools import format_security_results
        return format_security_results(filepath, vulnerabilities)
