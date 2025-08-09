class CodebaseAnalysisWorkflow:
    def __init__(self, agent):
        self.agent = agent
        self.analysis_results = {}
    
    def run_comprehensive_analysis(self, target_path: str = ".") -> str:
        """Run a comprehensive codebase analysis"""
        
        steps = [
            ("Project Structure", lambda: self._analyze_structure(target_path)),
            ("Code Quality", lambda: self._analyze_quality(target_path)),
            ("Complexity Analysis", lambda: self._analyze_complexity(target_path)),
            ("Dependencies", lambda: self._analyze_dependencies(target_path)),
            ("Test Coverage", lambda: self._analyze_tests(target_path))
        ]
        
        results = []
        for step_name, step_func in steps:
            try:
                result = step_func()
                self.analysis_results[step_name] = result
                results.append(f"✅ {step_name}: {result}")
            except Exception as e:
                results.append(f"❌ {step_name}: {e}")
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report()
        return report
    
    def _analyze_structure(self, path: str) -> str:
        """Analyze project structure"""
        structure_result = self.agent.parse_and_execute_tool(f'get_structure(directory="{path}")')
        
        if "❌" in structure_result:
            return "Failed to get project structure"
        
        # Parse structure for insights
        insights = []
        if "test" in structure_result.lower():
            insights.append("✅ Test directory found")
        else:
            insights.append("⚠️ No test directory detected")
        
        if "requirements.txt" in structure_result or "pyproject.toml" in structure_result:
            insights.append("✅ Dependency management found")
        else:
            insights.append("⚠️ No dependency management files")
        
        return f"Structure analyzed. {', '.join(insights)}"
    
    def _analyze_quality(self, path: str) -> str:
        """Analyze code quality"""
        quality_result = self.agent.parse_and_execute_tool(f'code_quality_report(directory="{path}")')
        
        if "❌" in quality_result:
            return "Code quality analysis failed"
        
        # Extract key metrics (simplified)
        if "excellent" in quality_result.lower():
            return "✅ High code quality detected"
        elif "good" in quality_result.lower():
            return "✅ Good code quality with minor issues"
        else:
            return "⚠️ Code quality needs improvement"
    
    def _analyze_complexity(self, path: str) -> str:
        """Analyze code complexity"""
        py_files = self.agent.parse_and_execute_tool(f'find_files(pattern="*.py", directory="{path}")')
        
        if "❌" in py_files:
            return "No Python files found"
        
        # Analyze key files
        complex_files = []
        file_list = py_files.split('\n')[:5]  # Analyze first 5 files
        
        for file_line in file_list:
            if '.py' in file_line:
                filepath = file_line.strip()
                complexity_result = self.agent.parse_and_execute_tool(f'analyze_complexity(filepath="{filepath}")')
                if "high complexity" in complexity_result.lower():
                    complex_files.append(filepath)
        
        if complex_files:
            return f"⚠️ High complexity in: {', '.join(complex_files)}"
        else:
            return "✅ Complexity levels are manageable"
    
    def _analyze_dependencies(self, path: str) -> str:
        """Analyze project dependencies"""
        req_result = self.agent.parse_and_execute_tool(f'read_file(filepath="{path}/requirements.txt")')
        
        if "❌" not in req_result:
            deps = len(req_result.split('\n'))
            return f"✅ {deps} dependencies found"
        else:
            return "ℹ️ No requirements.txt found"
    
    def _analyze_tests(self, path: str) -> str:
        """Analyze test coverage"""
        test_files = self.agent.parse_and_execute_tool(f'find_files(pattern="test_*.py", directory="{path}")')
        
        if "❌" not in test_files and test_files.strip():
            test_count = len(test_files.split('\n'))
            return f"✅ {test_count} test files found"
        else:
            return "⚠️ No test files detected"
    
    def _generate_comprehensive_report(self) -> str:
        """Generate a comprehensive analysis report"""
        
        report = """
# 📊 Comprehensive Codebase Analysis Report

## Summary
"""
        
        for analysis_type, result in self.analysis_results.items():
            status = "✅" if "✅" in result else "⚠️" if "⚠️" in result else "❌"
            report += f"- **{analysis_type}**: {status} {result}\n"
        
        report += """
## Recommendations

### High Priority
"""
        
        # Generate recommendations based on results
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report += f"- {rec}\n"
        
        return report
    
    def _generate_recommendations(self) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        for analysis_type, result in self.analysis_results.items():
            if "⚠️" in result or "❌" in result:
                if "test" in analysis_type.lower():
                    recommendations.append("🧪 Add comprehensive test suite")
                elif "quality" in analysis_type.lower():
                    recommendations.append("🔧 Run linting tools and fix style issues")
                elif "complexity" in analysis_type.lower():
                    recommendations.append("♻️ Refactor complex functions")
                elif "dependencies" in analysis_type.lower():
                    recommendations.append("📦 Add requirements.txt for dependency management")
        
        if not recommendations:
            recommendations.append("🎉 Codebase looks good! Consider adding documentation")
        
        return recommendations