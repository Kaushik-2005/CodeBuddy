"""
Security and Dependency Analysis Tools - Continuation of analysis_tools.py
"""
import ast
import os
import re
from typing import Dict, List, Optional, Any


def check_ast_security(tree: ast.AST) -> List[Dict[str, Any]]:
    """AST-based security checks"""
    vulnerabilities = []
    
    for node in ast.walk(tree):
        # Check for dangerous function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                
                if func_name in ['eval', 'exec', 'compile']:
                    vulnerabilities.append({
                        'type': 'dangerous_function',
                        'line': node.lineno,
                        'message': f"Dangerous function '{func_name}' can execute arbitrary code",
                        'severity': 'high'
                    })
            
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr == 'loads' and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'pickle':
                        vulnerabilities.append({
                            'type': 'pickle_security',
                            'line': node.lineno,
                            'message': "pickle.loads() can execute arbitrary code",
                            'severity': 'high'
                        })
        
        # Check for assert statements (can be disabled with -O)
        if isinstance(node, ast.Assert):
            vulnerabilities.append({
                'type': 'assert_security',
                'line': node.lineno,
                'message': "Assert statements are removed with -O optimization",
                'severity': 'low'
            })
    
    return vulnerabilities


def format_security_results(filepath: str, vulnerabilities: List[Dict[str, Any]]) -> str:
    """Format security scan results"""
    if not vulnerabilities:
        return f"🛡️ **{filepath}**: No security vulnerabilities detected! 🎉"
    
    lines = [f"🔒 **Security Scan Results for {filepath}:**\n"]
    
    # Group by severity
    high = [v for v in vulnerabilities if v['severity'] == 'high']
    medium = [v for v in vulnerabilities if v['severity'] == 'medium']
    low = [v for v in vulnerabilities if v['severity'] == 'low']
    
    if high:
        lines.append("🚨 **High Severity:**")
        for vuln in high:
            lines.append(f"  • Line {vuln['line']}: {vuln['message']}")
            if 'code' in vuln:
                lines.append(f"    Code: `{vuln['code']}`")
        lines.append("")
    
    if medium:
        lines.append("⚠️ **Medium Severity:**")
        for vuln in medium:
            lines.append(f"  • Line {vuln['line']}: {vuln['message']}")
            if 'code' in vuln:
                lines.append(f"    Code: `{vuln['code']}`")
        lines.append("")
    
    if low:
        lines.append("ℹ️ **Low Severity:**")
        for vuln in low:
            lines.append(f"  • Line {vuln['line']}: {vuln['message']}")
        lines.append("")
    
    # Summary and recommendations
    total = len(vulnerabilities)
    lines.append(f"📊 **Summary**: {len(high)} high, {len(medium)} medium, {len(low)} low ({total} total)")
    
    if high:
        lines.append("\n🔧 **Immediate Actions Required:**")
        lines.append("  • Review and fix high-severity vulnerabilities immediately")
        lines.append("  • Consider using parameterized queries for database operations")
        lines.append("  • Use subprocess with shell=False and validate inputs")
        lines.append("  • Store secrets in environment variables or secure vaults")
    
    return '\n'.join(lines)


class DependencyAnalyzerTool:
    """Analyze project dependencies for security and updates"""
    
    def execute(self, directory: str = ".") -> str:
        """Analyze project dependencies"""
        try:
            # Look for requirements files
            req_files = ['requirements.txt', 'requirements-dev.txt', 'Pipfile', 'pyproject.toml']
            found_files = []
            
            for req_file in req_files:
                full_path = os.path.join(directory, req_file)
                if os.path.exists(full_path):
                    found_files.append(req_file)
            
            if not found_files:
                return "ℹ️ No dependency files found (requirements.txt, Pipfile, pyproject.toml)"
            
            results = []
            for req_file in found_files:
                result = self._analyze_requirements_file(os.path.join(directory, req_file))
                results.append(f"📦 **{req_file}:**\n{result}")
            
            return '\n\n'.join(results)
            
        except Exception as e:
            return f"❌ Dependency analysis failed: {e}"
    
    def _analyze_requirements_file(self, filepath: str) -> str:
        """Analyze a requirements file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            if not lines:
                return "  No dependencies found"
            
            dependencies = []
            issues = []
            
            for line in lines:
                # Parse dependency line
                dep_info = self._parse_dependency(line)
                if dep_info:
                    dependencies.append(dep_info)
                    
                    # Check for potential issues
                    if not dep_info['version']:
                        issues.append(f"  ⚠️ {dep_info['name']}: No version specified (unpinned dependency)")
                    elif dep_info['version'].startswith('>='):
                        issues.append(f"  ⚠️ {dep_info['name']}: Using >= version constraint (potential compatibility issues)")
            
            result_lines = [f"  📊 Found {len(dependencies)} dependencies"]
            
            if issues:
                result_lines.append("  \n  🔍 **Issues:**")
                result_lines.extend(issues)
            
            # Check for known risky packages (simplified)
            risky_packages = ['pickle', 'eval', 'exec', 'os.system']
            for dep in dependencies:
                if any(risky in dep['name'].lower() for risky in risky_packages):
                    result_lines.append(f"  🚨 {dep['name']}: Potentially risky package")
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            return f"  ❌ Error analyzing {filepath}: {e}"
    
    def _parse_dependency(self, line: str) -> Optional[Dict[str, str]]:
        """Parse a dependency line"""
        # Handle different formats: package==1.0, package>=1.0, package, etc.
        match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+.*)?', line)
        if match:
            name = match.group(1)
            version = match.group(2) if match.group(2) else ""
            return {'name': name, 'version': version}
        return None


class CodeQualityTool:
    """Overall code quality assessment"""
    
    def execute(self, filepath: str, directory: str = ".") -> str:
        """Perform comprehensive code quality analysis"""
        try:
            full_path = os.path.join(directory, filepath)
            
            if not os.path.exists(full_path):
                return f"❌ File not found: {filepath}"
            
            if not filepath.endswith('.py'):
                return f"❌ Not a Python file: {filepath}"
            
            # Import the analysis tools
            from .analysis_tools import PythonLinterTool, ComplexityAnalyzerTool, SecurityScannerTool
            
            # Run all analyses
            linter = PythonLinterTool()
            complexity = ComplexityAnalyzerTool()
            security = SecurityScannerTool()
            
            lint_result = linter.execute(filepath, directory)
            complexity_result = complexity.execute(filepath, directory)
            security_result = security.execute(filepath, directory)
            
            # Combine results
            lines = [f"🎯 **Comprehensive Code Quality Report for {filepath}:**\n"]
            
            # Extract scores and issues
            lint_issues = self._extract_issue_count(lint_result)
            security_issues = self._extract_security_count(security_result)
            
            # Overall quality score
            quality_score = self._calculate_quality_score(lint_issues, security_issues)
            score_emoji = "🟢" if quality_score >= 80 else "🟡" if quality_score >= 60 else "🔴"
            
            lines.append(f"📊 **Overall Quality Score: {quality_score}/100** {score_emoji}\n")
            
            # Individual reports
            lines.append("=" * 60)
            lines.append(lint_result)
            lines.append("\n" + "=" * 60)
            lines.append(complexity_result)
            lines.append("\n" + "=" * 60)
            lines.append(security_result)
            
            # Final recommendations
            lines.append("\n" + "=" * 60)
            lines.append("🎯 **Final Recommendations:**")
            
            if quality_score >= 90:
                lines.append("  ✅ Excellent code quality! Keep up the good work!")
            elif quality_score >= 80:
                lines.append("  👍 Good code quality with minor improvements needed")
            elif quality_score >= 60:
                lines.append("  ⚠️ Moderate code quality - several issues to address")
            else:
                lines.append("  🚨 Poor code quality - immediate attention required")
            
            return '\n'.join(lines)
            
        except Exception as e:
            return f"❌ Code quality analysis failed: {e}"
    
    def _extract_issue_count(self, lint_result: str) -> Dict[str, int]:
        """Extract issue counts from lint result"""
        errors = len(re.findall(r'🔴', lint_result))
        warnings = len(re.findall(r'🟡', lint_result))
        info = len(re.findall(r'🔵', lint_result))
        return {'errors': errors, 'warnings': warnings, 'info': info}
    
    def _extract_security_count(self, security_result: str) -> Dict[str, int]:
        """Extract security issue counts"""
        high = len(re.findall(r'🚨', security_result))
        medium = len(re.findall(r'⚠️', security_result))
        low = len(re.findall(r'ℹ️', security_result))
        return {'high': high, 'medium': medium, 'low': low}
    
    def _calculate_quality_score(self, lint_issues: Dict[str, int], security_issues: Dict[str, int]) -> int:
        """Calculate overall quality score"""
        score = 100
        
        # Deduct for lint issues
        score -= lint_issues['errors'] * 10
        score -= lint_issues['warnings'] * 5
        score -= lint_issues['info'] * 1
        
        # Deduct for security issues
        score -= security_issues['high'] * 20
        score -= security_issues['medium'] * 10
        score -= security_issues['low'] * 2
        
        return max(0, score)
