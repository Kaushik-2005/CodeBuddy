import os
import fnmatch
from pathlib import Path

def read_file(filepath: str) -> str:
    """Read file contents with enhanced path resolution"""
    try:
        # Expand environment variables and user home
        expanded_path = os.path.expandvars(os.path.expanduser(filepath))
        
        # Convert to absolute path
        abs_path = os.path.abspath(expanded_path)
        
        if not os.path.exists(abs_path):
            return f"❌ File not found: {abs_path}"
        
        if not os.path.isfile(abs_path):
            return f"❌ Path is not a file: {abs_path}"
        
        # Check file size (limit to 1MB for safety)
        file_size = os.path.getsize(abs_path)
        if file_size > 1024 * 1024:  # 1MB
            return f"❌ File too large ({file_size} bytes). Maximum size is 1MB."
        
        # Try to read with different encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(abs_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content  # Return just content for regular use
            except UnicodeDecodeError:
                continue
        
        return f"❌ Could not decode file {abs_path} with common encodings"
        
    except Exception as e:
        return f"❌ Error reading file: {e}"

def write_file(filepath: str, content: str) -> str:
    """Create or overwrite a file with content"""
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Unescape content
        content = content.replace('\\n', '\n').replace('\\"', '"')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Successfully wrote to {filepath}"
    
    except Exception as e:
        return f"❌ Error writing file: {e}"

def search_codebase(search_term: str, directory: str = ".") -> str:
    """Search for a term across all files in directory"""
    try:
        matches = []
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.md', '.txt', '.java', '.cpp', '.c')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        for line_num, line in enumerate(lines, 1):
                            if search_term.lower() in line.lower():
                                matches.append({
                                    'file': filepath,
                                    'line': line_num,
                                    'content': line.strip()
                                })
                    except:
                        continue
        
        if matches:
            result = f"Found {len(matches)} matches for '{search_term}':\n\n"
            for match in matches[:20]:  # Limit to first 20 results
                result += f"📁 {match['file']}:{match['line']}\n"
                result += f"   {match['content']}\n\n"
            return result
        else:
            return f"No matches found for '{search_term}'"
    
    except Exception as e:
        return f"❌ Error searching: {e}"

def get_structure(directory: str = ".") -> str:
    """Get directory structure as a tree"""
    try:
        def build_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth > max_depth:
                return ""
            
            items = []
            try:
                for item in sorted(os.listdir(path)):
                    if item.startswith('.') and item not in ['.env', '.gitignore']:
                        continue
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        if item in ['__pycache__', 'node_modules', '.git', '.venv']:
                            continue
                        items.append((item, True))
                    else:
                        items.append((item, False))
            except PermissionError:
                return f"{prefix}❌ Permission denied\n"
            
            tree = ""
            for i, (item, is_dir) in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                icon = "📁" if is_dir else "📄"
                
                tree += f"{prefix}{current_prefix}{icon} {item}\n"
                
                if is_dir and current_depth < max_depth:
                    extension = "    " if is_last else "│   "
                    item_path = os.path.join(path, item)
                    tree += build_tree(item_path, prefix + extension, max_depth, current_depth + 1)
            
            return tree
        
        result = f"📂 Directory structure for {os.path.abspath(directory)}:\n\n"
        result += build_tree(directory)
        return result
    
    except Exception as e:
        return f"❌ Error getting structure: {e}"

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

def create_directory(directory_path: str) -> str:
    """Create a directory"""
    try:
        if os.path.exists(directory_path):
            return f"Directory {directory_path} already exists"
        
        os.makedirs(directory_path, exist_ok=True)
        return f"✅ Successfully created directory: {directory_path}"
    
    except Exception as e:
        return f"❌ Error creating directory: {e}"

def delete_directory(directory_path: str) -> str:
    """Delete a directory and all its contents (with safety checks)"""
    try:
        import shutil
        
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

def find_files(pattern: str, directory: str = ".", max_results: int = 20) -> str:
    """Find files matching a pattern"""
    try:
        # Expand the directory path
        expanded_dir = os.path.expandvars(os.path.expanduser(directory))
        
        if not os.path.exists(expanded_dir):
            return f"❌ Directory not found: {expanded_dir}"
        
        matches = []
        
        for root, dirs, files in os.walk(expanded_dir):
            # Skip common directories to avoid clutter
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    full_path = os.path.join(root, file)
                    file_size = os.path.getsize(full_path)
                    matches.append((full_path, file_size))
                    
                    if len(matches) >= max_results:
                        break
            
            if len(matches) >= max_results:
                break
        
        if matches:
            result = f"🔍 Found {len(matches)} files matching '{pattern}':\n\n"
            for filepath, size in matches:
                result += f"📁 {filepath} ({size} bytes)\n"
            
            if len(matches) == max_results:
                result += f"\n... (limited to {max_results} results)"
                
            return result
        else:
            return f"❌ No files found matching pattern '{pattern}' in {expanded_dir}"
    
    except Exception as e:
        return f"❌ Error finding files: {e}"

def get_file_info(filepath: str) -> str:
    """Get detailed information about a file"""
    try:
        expanded_path = os.path.expandvars(os.path.expanduser(filepath))
        abs_path = os.path.abspath(expanded_path)
        
        if not os.path.exists(abs_path):
            return f"❌ File not found: {abs_path}"
        
        stat = os.stat(abs_path)
        
        info = f"📄 File Information: {abs_path}\n"
        info += f"📏 Size: {stat.st_size} bytes\n"
        info += f"📅 Modified: {Path(abs_path).stat().st_mtime}\n"
        info += f"🔧 Extension: {Path(abs_path).suffix}\n"
        info += f"📂 Directory: {Path(abs_path).parent}\n"
        
        if os.path.isfile(abs_path):
            info += f"📝 Type: Regular file\n"
        elif os.path.isdir(abs_path):
            info += f"📁 Type: Directory\n"
        
        # Check if it's a text file
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                f.read(100)
            info += f"✅ Text file (readable)\n"
        except:
            info += f"🔒 Binary file or unreadable\n"
        
        return info
        
    except Exception as e:
        return f"❌ Error getting file info: {e}"