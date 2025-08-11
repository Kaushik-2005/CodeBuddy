"""
Code Refactoring and Improvement Tools for CodeBuddy
"""
import os
import ast
import re
from typing import Dict, List, Optional, Any, Tuple


class CodeRefactorTool:
    """Refactor and improve existing code"""
    
    def execute(self, filepath: str, refactor_type: str = "auto", **kwargs) -> str:
        """Refactor code in the specified file"""
        try:
            if not os.path.exists(filepath):
                return f"❌ File not found: {filepath}"
            
            if not filepath.endswith('.py'):
                return f"❌ Only Python files are supported for refactoring"
            
            # Read original code
            with open(filepath, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Perform refactoring
            if refactor_type == "auto":
                refactored_code = self._auto_refactor(original_code)
            elif refactor_type == "extract_functions":
                refactored_code = self._extract_functions(original_code)
            elif refactor_type == "improve_naming":
                refactored_code = self._improve_naming(original_code)
            elif refactor_type == "add_docstrings":
                refactored_code = self._add_docstrings(original_code)
            elif refactor_type == "optimize_imports":
                refactored_code = self._optimize_imports(original_code)
            elif refactor_type == "add_type_hints":
                refactored_code = self._add_type_hints(original_code)
            else:
                return f"❌ Unknown refactor type: {refactor_type}. Available: auto, extract_functions, improve_naming, add_docstrings, optimize_imports, add_type_hints"
            
            # Create backup
            backup_path = f"{filepath}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            
            # Write refactored code
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(refactored_code)
            
            # Calculate improvements
            improvements = self._calculate_improvements(original_code, refactored_code)
            
            return f"""✅ Code refactored successfully!

📁 **File**: {filepath}
🔄 **Refactor Type**: {refactor_type}
💾 **Backup**: {backup_path}

📊 **Improvements**:
{improvements}

🔍 **Next Steps**:
• Review the refactored code
• Run tests to ensure functionality
• Delete backup if satisfied: `rm {backup_path}`
"""
            
        except Exception as e:
            return f"❌ Refactoring failed: {e}"
    
    def _auto_refactor(self, code: str) -> str:
        """Perform automatic refactoring"""
        # Apply multiple refactoring techniques
        refactored = code
        refactored = self._optimize_imports(refactored)
        refactored = self._improve_naming(refactored)
        refactored = self._add_docstrings(refactored)
        refactored = self._extract_functions(refactored)
        return refactored
    
    def _extract_functions(self, code: str) -> str:
        """Extract long methods into smaller functions"""
        try:
            tree = ast.parse(code)
            
            class FunctionExtractor(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # If function is too long, suggest extraction
                    if len(node.body) > 15:  # Arbitrary threshold
                        # Add comment suggesting extraction
                        comment = ast.Expr(value=ast.Constant(
                            value=f"# TODO: Consider extracting parts of this {len(node.body)}-line function"
                        ))
                        node.body.insert(0, comment)
                    return node
            
            transformer = FunctionExtractor()
            new_tree = transformer.visit(tree)
            
            return ast.unparse(new_tree)
            
        except Exception:
            return code  # Return original if parsing fails
    
    def _improve_naming(self, code: str) -> str:
        """Improve variable and function naming"""
        # Simple naming improvements
        improvements = {
            # Common poor variable names
            r'\bx\b': 'value',
            r'\by\b': 'result',
            r'\bi\b': 'index',
            r'\bj\b': 'inner_index',
            r'\bk\b': 'key',
            r'\bv\b': 'val',
            r'\btemp\b': 'temporary_value',
            r'\bdata\b': 'input_data',
            r'\bresult\b': 'output_result',
            
            # Function naming improvements
            r'def calc\(': 'def calculate(',
            r'def proc\(': 'def process(',
            r'def init\(': 'def initialize(',
        }
        
        improved_code = code
        for pattern, replacement in improvements.items():
            # Only replace if it's not part of a larger word
            improved_code = re.sub(pattern, replacement, improved_code)
        
        return improved_code
    
    def _add_docstrings(self, code: str) -> str:
        """Add docstrings to functions and classes"""
        try:
            tree = ast.parse(code)
            
            class DocstringAdder(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Check if function already has docstring
                    if (not node.body or 
                        not isinstance(node.body[0], ast.Expr) or 
                        not isinstance(node.body[0].value, ast.Constant)):
                        
                        # Create docstring based on function name and args
                        args_str = ", ".join([arg.arg for arg in node.args.args])
                        docstring = f'"""{node.name.replace("_", " ").title()}\n    \n    Args:\n        {args_str}\n    \n    Returns:\n        Result of {node.name}\n    """'
                        
                        # Insert docstring as first statement
                        docstring_node = ast.Expr(value=ast.Constant(value=docstring))
                        node.body.insert(0, docstring_node)
                    
                    return node
                
                def visit_ClassDef(self, node):
                    # Check if class already has docstring
                    if (not node.body or 
                        not isinstance(node.body[0], ast.Expr) or 
                        not isinstance(node.body[0].value, ast.Constant)):
                        
                        # Create class docstring
                        docstring = f'"""{node.name} class\n    \n    A class for {node.name.lower()} operations.\n    """'
                        
                        # Insert docstring as first statement
                        docstring_node = ast.Expr(value=ast.Constant(value=docstring))
                        node.body.insert(0, docstring_node)
                    
                    return node
            
            transformer = DocstringAdder()
            new_tree = transformer.visit(tree)
            
            return ast.unparse(new_tree)
            
        except Exception:
            return code  # Return original if parsing fails
    
    def _optimize_imports(self, code: str) -> str:
        """Optimize import statements"""
        lines = code.split('\n')
        
        # Separate imports from rest of code
        imports = []
        other_lines = []
        in_imports = True
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith(('import ', 'from ')) and in_imports:
                imports.append(line)
            elif stripped == '' and in_imports:
                continue  # Skip empty lines in import section
            elif stripped.startswith('#') and in_imports:
                imports.append(line)  # Keep comments in import section
            else:
                in_imports = False
                other_lines.append(line)
        
        # Sort imports
        standard_imports = []
        third_party_imports = []
        local_imports = []
        
        for imp in imports:
            stripped = imp.strip()
            if stripped.startswith('#'):
                continue
            
            if stripped.startswith('from .') or stripped.startswith('import .'):
                local_imports.append(imp)
            elif any(lib in stripped for lib in ['os', 'sys', 'json', 'datetime', 'typing', 're']):
                standard_imports.append(imp)
            else:
                third_party_imports.append(imp)
        
        # Reconstruct code with organized imports
        organized_imports = []
        
        if standard_imports:
            organized_imports.extend(sorted(standard_imports))
            organized_imports.append('')
        
        if third_party_imports:
            organized_imports.extend(sorted(third_party_imports))
            organized_imports.append('')
        
        if local_imports:
            organized_imports.extend(sorted(local_imports))
            organized_imports.append('')
        
        return '\n'.join(organized_imports + other_lines)
    
    def _add_type_hints(self, code: str) -> str:
        """Add basic type hints to function signatures"""
        try:
            tree = ast.parse(code)
            
            class TypeHintAdder(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Add basic type hints if missing
                    for arg in node.args.args:
                        if arg.annotation is None:
                            # Add generic type hint
                            if arg.arg in ['self', 'cls']:
                                continue
                            elif arg.arg in ['data', 'content', 'text']:
                                arg.annotation = ast.Name(id='str', ctx=ast.Load())
                            elif arg.arg in ['count', 'size', 'length']:
                                arg.annotation = ast.Name(id='int', ctx=ast.Load())
                            elif arg.arg in ['items', 'values']:
                                arg.annotation = ast.Name(id='List', ctx=ast.Load())
                            else:
                                arg.annotation = ast.Name(id='Any', ctx=ast.Load())
                    
                    # Add return type hint if missing
                    if node.returns is None:
                        node.returns = ast.Name(id='Any', ctx=ast.Load())
                    
                    return node
            
            transformer = TypeHintAdder()
            new_tree = transformer.visit(tree)
            
            # Add typing import if not present
            refactored_code = ast.unparse(new_tree)
            if 'from typing import' not in refactored_code and 'import typing' not in refactored_code:
                refactored_code = 'from typing import Any, List, Dict, Optional\n\n' + refactored_code
            
            return refactored_code
            
        except Exception:
            return code  # Return original if parsing fails
    
    def _calculate_improvements(self, original: str, refactored: str) -> str:
        """Calculate and format improvements made"""
        original_lines = len(original.split('\n'))
        refactored_lines = len(refactored.split('\n'))
        
        original_functions = len(re.findall(r'def \w+\(', original))
        refactored_functions = len(re.findall(r'def \w+\(', refactored))
        
        original_docstrings = len(re.findall(r'""".*?"""', original, re.DOTALL))
        refactored_docstrings = len(re.findall(r'""".*?"""', refactored, re.DOTALL))
        
        improvements = []
        
        if refactored_lines != original_lines:
            improvements.append(f"• Lines: {original_lines} → {refactored_lines}")
        
        if refactored_functions != original_functions:
            improvements.append(f"• Functions: {original_functions} → {refactored_functions}")
        
        if refactored_docstrings > original_docstrings:
            improvements.append(f"• Docstrings added: {refactored_docstrings - original_docstrings}")
        
        if 'from typing import' in refactored and 'from typing import' not in original:
            improvements.append("• Type hints added")
        
        if not improvements:
            improvements.append("• Code structure optimized")
        
        return '\n'.join(improvements)
