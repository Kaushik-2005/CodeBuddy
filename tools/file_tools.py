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

def delete_directory(directory_path: str) -> str:
    """Delete a directory and all its contents (with safety checks)"""
    try:
        if not os.path.exists(directory_path):
            return f"Directory {directory_path} does not exist"
        
        if not os.path.isdir(directory_path):
            return f"{directory_path} is not a directory"
        
        # Safety check - don't delete important directories
        dangerous_dirs = [
            '.git', '.env', 'node_modules', '__pycache__', 
            '.', '..', '/', 'C:\\', 'D:\\', 'E:\\',
            os.path.expanduser('~'), # Home directory
            os.getcwd()  # Current working directory
        ]
        
        abs_path = os.path.abspath(directory_path)
        for dangerous in dangerous_dirs:
            if abs_path == os.path.abspath(dangerous):
                return f"Cannot delete protected directory: {directory_path}"
        
        # Additional safety - don't delete if it contains important files
        important_files = ['.env', 'main.py', 'requirements.txt', '.gitignore']
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file in important_files:
                    return f"Cannot delete directory containing important file: {file}"
        
        # Count items to delete
        total_items = sum([len(dirs) + len(files) for _, dirs, files in os.walk(directory_path)])
        
        # Delete the directory
        shutil.rmtree(directory_path)
        
        return f"✅ Successfully deleted directory '{directory_path}' ({total_items} items removed)"
        
    except PermissionError:
        return f"❌ Permission denied: Cannot delete '{directory_path}'. It may be in use or you may not have sufficient permissions."
    except Exception as e:
        return f"❌ Error deleting directory: {e}"

def delete_file(filepath: str) -> str:
    """Delete a file (with safety check)"""
    try:
        if not os.path.exists(filepath):
            return f"File {filepath} does not exist"
        
        if os.path.isdir(filepath):
            return f"❌ '{filepath}' is a directory. Use delete_directory instead."
        
        # Safety check - don't delete important files
        dangerous_files = ['.env', 'requirements.txt', 'main.py']
        if os.path.basename(filepath) in dangerous_files:
            return f"Cannot delete important file: {filepath}"
        
        os.remove(filepath)
        return f"✅ Successfully deleted file: {filepath}"
        
    except Exception as e:
        return f"❌ Error deleting file: {e}"

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