"""
File Operations Tools - Safe file system interactions
"""
import os
from typing import Dict, List
from .base_tool import BaseTool, ToolResult


class ReadFileTool(BaseTool):
    """Tool for reading file contents"""
    
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read and display file contents"
        )
    
    def execute(self, filepath: str, **kwargs) -> ToolResult:
        """Read a file and return its contents"""
        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    message=f"❌ File not found: {filepath}"
                )
            
            if not os.path.isfile(filepath):
                return ToolResult(
                    success=False,
                    message=f"❌ Path is not a file: {filepath}"
                )
            
            # Check file size (safety check)
            file_size = os.path.getsize(filepath)
            if file_size > 1024 * 1024:  # 1MB limit
                return ToolResult(
                    success=False,
                    message=f"❌ File too large: {filepath} ({file_size} bytes)"
                )
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Format output nicely
            lines = content.split('\n')
            line_count = len(lines)
            
            formatted_content = f"📄 **{filepath}** ({line_count} lines)\n"
            formatted_content += "─" * 50 + "\n"
            
            # Add line numbers for better readability
            for i, line in enumerate(lines[:100], 1):  # Limit to first 100 lines
                formatted_content += f"{i:3d} | {line}\n"
            
            if line_count > 100:
                formatted_content += f"... ({line_count - 100} more lines)\n"
            
            return ToolResult(
                success=True,
                message=formatted_content,
                data={"content": content, "lines": line_count, "size": file_size}
            )
            
        except UnicodeDecodeError:
            return ToolResult(
                success=False,
                message=f"❌ Cannot read file (binary or encoding issue): {filepath}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error reading file: {e}"
            )
    
    def get_parameters(self) -> Dict[str, str]:
        return {"filepath": "Path to the file to read"}


class WriteFileTool(BaseTool):
    """Tool for writing file contents with approval"""
    
    def __init__(self):
        super().__init__(
            name="write_file", 
            description="Write content to a file (requires approval)"
        )
    
    def execute(self, filepath: str, content: str, **kwargs) -> ToolResult:
        """Write content to a file"""
        try:
            # Check if file exists (for approval decision)
            file_exists = os.path.exists(filepath)
            
            # Create directory if needed
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Write the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Calculate stats
            lines = len(content.split('\n'))
            size = len(content.encode('utf-8'))
            
            action = "Updated" if file_exists else "Created"
            
            return ToolResult(
                success=True,
                message=f"✅ {action} {filepath} ({lines} lines, {size} bytes)",
                data={"filepath": filepath, "lines": lines, "size": size},
                requires_approval=True  # File writing requires approval
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error writing file: {e}"
            )
    
    def get_parameters(self) -> Dict[str, str]:
        return {
            "filepath": "Path to the file to write",
            "content": "Content to write to the file"
        }


class ListFilesTool(BaseTool):
    """Tool for listing directory contents"""
    
    def __init__(self):
        super().__init__(
            name="list_files",
            description="List files and directories"
        )
    
    def execute(self, directory: str = ".", **kwargs) -> ToolResult:
        """List directory contents"""
        try:
            if not os.path.exists(directory):
                return ToolResult(
                    success=False,
                    message=f"❌ Directory not found: {directory}"
                )
            
            if not os.path.isdir(directory):
                return ToolResult(
                    success=False,
                    message=f"❌ Path is not a directory: {directory}"
                )
            
            items = []
            for item in sorted(os.listdir(directory)):
                if item.startswith('.'):
                    continue  # Skip hidden files
                
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    items.append(f"📄 {item} ({size} bytes)")
            
            if not items:
                return ToolResult(
                    success=True,
                    message=f"📂 Directory {directory} is empty"
                )
            
            result = f"📂 **{directory}**\n"
            result += "\n".join(items)
            
            return ToolResult(
                success=True,
                message=result,
                data={"directory": directory, "item_count": len(items)}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error listing directory: {e}"
            )
    
    def get_parameters(self) -> Dict[str, str]:
        return {"directory": "Directory to list (default: current directory)"}


class CreateFolderTool(BaseTool):
    """Tool for creating directories"""

    def __init__(self):
        super().__init__(
            name="create_folder",
            description="Create a new directory/folder"
        )

    def execute(self, folderpath: str, **kwargs) -> ToolResult:
        """Create a directory"""
        try:
            if os.path.exists(folderpath):
                return ToolResult(
                    success=False,
                    message=f"❌ Folder already exists: {folderpath}"
                )

            os.makedirs(folderpath, exist_ok=True)

            return ToolResult(
                success=True,
                message=f"✅ Created folder: {folderpath}",
                data={"folderpath": folderpath}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error creating folder: {e}"
            )

    def get_parameters(self) -> Dict[str, str]:
        return {"folderpath": "Path of the folder to create"}


class DeleteFileTool(BaseTool):
    """Tool for deleting files (requires approval)"""

    def __init__(self):
        super().__init__(
            name="delete_file",
            description="Delete a file (requires approval)"
        )

    def execute(self, filepath: str, **kwargs) -> ToolResult:
        """Delete a file"""
        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    message=f"❌ File not found: {filepath}"
                )

            if not os.path.isfile(filepath):
                return ToolResult(
                    success=False,
                    message=f"❌ Path is not a file: {filepath}"
                )

            # Get file info before deletion
            file_size = os.path.getsize(filepath)

            os.remove(filepath)

            return ToolResult(
                success=True,
                message=f"✅ Deleted file: {filepath} ({file_size} bytes)",
                data={"filepath": filepath, "size": file_size},
                requires_approval=True  # File deletion requires approval
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error deleting file: {e}"
            )

    def get_parameters(self) -> Dict[str, str]:
        return {"filepath": "Path of the file to delete"}


class DeleteFolderTool(BaseTool):
    """Tool for deleting directories (requires approval)"""

    def __init__(self):
        super().__init__(
            name="delete_folder",
            description="Delete a directory/folder (requires approval)"
        )

    def execute(self, folderpath: str, **kwargs) -> ToolResult:
        """Delete a directory"""
        try:
            if not os.path.exists(folderpath):
                return ToolResult(
                    success=False,
                    message=f"❌ Folder not found: {folderpath}"
                )

            if not os.path.isdir(folderpath):
                return ToolResult(
                    success=False,
                    message=f"❌ Path is not a directory: {folderpath}"
                )

            # Count items before deletion
            import shutil
            try:
                item_count = len(os.listdir(folderpath))
                shutil.rmtree(folderpath)

                return ToolResult(
                    success=True,
                    message=f"✅ Deleted folder: {folderpath} ({item_count} items)",
                    data={"folderpath": folderpath, "item_count": item_count},
                    requires_approval=True  # Folder deletion requires approval
                )
            except OSError as e:
                if "not empty" in str(e).lower():
                    return ToolResult(
                        success=False,
                        message=f"❌ Folder not empty: {folderpath}. Use force=true to delete non-empty folders.",
                        requires_approval=True
                    )
                raise e

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"❌ Error deleting folder: {e}"
            )

    def get_parameters(self) -> Dict[str, str]:
        return {"folderpath": "Path of the folder to delete"}


# Tool factory functions for easy registration
def create_file_tools() -> List[BaseTool]:
    """Create all file operation tools"""
    return [
        ReadFileTool(),
        WriteFileTool(),
        ListFilesTool(),
        CreateFolderTool(),
        DeleteFileTool(),
        DeleteFolderTool()
    ]
