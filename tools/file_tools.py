import os
import shutil
from pathlib import Path

def read_file(filepath: str) -> str:
    """Read content from a file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(filepath: str, content: str) -> str:
    """Write content to a file"""
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # Process content to handle escaped characters
        processed_content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace("\\'", "'")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(processed_content)
        
        return f"Successfully wrote to {filepath}"
        
    except Exception as e:
        return f"Error writing file: {e}"

def delete_file(filepath: str) -> str:
    """Delete a file (with safety check)"""
    try:
        if not os.path.exists(filepath):
            return f"File {filepath} does not exist"
        
        # Safety check - don't delete important files
        dangerous_files = ['.env', 'requirements.txt', 'main.py']
        if os.path.basename(filepath) in dangerous_files:
            return f"Cannot delete important file: {filepath}"
        
        os.remove(filepath)
        return f"Successfully deleted {filepath}"
        
    except Exception as e:
        return f"Error deleting file: {e}"

def search_codebase(search_term: str, directory: str = ".", file_extensions: list = None) -> str:
    """Search for a term across files in the codebase"""
    try:
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.md', '.txt']
        
        results = []
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if search_term.lower() in content.lower():
                                lines = content.split('\n')
                                matching_lines = []
                                for i, line in enumerate(lines, 1):
                                    if search_term.lower() in line.lower():
                                        matching_lines.append(f"  Line {i}: {line.strip()}")
                                
                                if matching_lines:
                                    results.append(f"\n{filepath}:")
                                    results.extend(matching_lines[:5])  # Limit to 5 matches per file
                    except:
                        continue  # Skip files that can't be read
        
        if results:
            return "\n".join(results)
        else:
            return f"No matches found for '{search_term}'"
    except Exception as e:
        return f"Error searching codebase: {e}"

def get_structure(directory: str = ".", max_depth: int = 3) -> str:
    """Get directory structure as a tree"""
    try:
        def build_tree(path, prefix="", depth=0):
            if depth > max_depth:
                return []
            
            items = []
            path_obj = Path(path)
            
            # Skip common directories
            skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', '.env'}
            
            try:
                entries = sorted(path_obj.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                for i, entry in enumerate(entries):
                    if entry.name.startswith('.') and entry.name not in {'.env', '.gitignore'}:
                        continue
                    if entry.name in skip_dirs:
                        continue
                        
                    is_last = i == len(entries) - 1
                    current_prefix = "└── " if is_last else "├── "
                    items.append(f"{prefix}{current_prefix}{entry.name}")
                    
                    if entry.is_dir() and depth < max_depth:
                        extension = "    " if is_last else "│   "
                        items.extend(build_tree(entry, prefix + extension, depth + 1))
            except PermissionError:
                items.append(f"{prefix}├── [Permission Denied]")
            
            return items
        
        tree = [directory + "/"]
        tree.extend(build_tree(directory))
        return "\n".join(tree)
    except Exception as e:
        return f"Error getting directory structure: {e}"

def create_directory(directory_path: str) -> str:
    """Create a directory"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return f"Successfully created directory: {directory_path}"
    except Exception as e:
        return f"Error creating directory: {e}"