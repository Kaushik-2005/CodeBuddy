"""
Git Operations Tools - Version control integration
"""
import subprocess
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class GitStatus:
    """Git repository status information"""
    branch: str
    ahead: int
    behind: int
    staged: List[str]
    modified: List[str]
    untracked: List[str]
    clean: bool


class GitStatusTool:
    """Check Git repository status"""
    
    def execute(self, directory: str = ".") -> str:
        """Get Git status for repository"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return "❌ Not a Git repository"
            
            # Get detailed status
            status = self._get_git_status(directory)
            return self._format_status(status)
            
        except subprocess.TimeoutExpired:
            return "❌ Git command timeout"
        except Exception as e:
            return f"❌ Git status failed: {e}"
    
    def _get_git_status(self, directory: str) -> GitStatus:
        """Get detailed Git status information"""
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=directory,
            capture_output=True,
            text=True
        )
        branch = branch_result.stdout.strip() or "HEAD"
        
        # Get ahead/behind info
        ahead, behind = self._get_ahead_behind(directory)
        
        # Get file status
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=directory,
            capture_output=True,
            text=True
        )
        
        staged = []
        modified = []
        untracked = []
        
        for line in status_result.stdout.strip().split('\n'):
            if not line:
                continue
                
            status_code = line[:2]
            filename = line[3:]
            
            if status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                staged.append(f"{status_code[0]} {filename}")
            if status_code[1] in ['M', 'D']:
                modified.append(f"{status_code[1]} {filename}")
            if status_code == '??':
                untracked.append(filename)
        
        clean = not (staged or modified or untracked)
        
        return GitStatus(
            branch=branch,
            ahead=ahead,
            behind=behind,
            staged=staged,
            modified=modified,
            untracked=untracked,
            clean=clean
        )
    
    def _get_ahead_behind(self, directory: str) -> Tuple[int, int]:
        """Get ahead/behind commit count"""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
                cwd=directory,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                ahead, behind = map(int, result.stdout.strip().split())
                return ahead, behind
        except:
            pass
        
        return 0, 0
    
    def _format_status(self, status: GitStatus) -> str:
        """Format Git status for display"""
        lines = []
        
        # Branch info
        branch_info = f"📍 **Branch:** {status.branch}"
        if status.ahead > 0:
            branch_info += f" (ahead {status.ahead})"
        if status.behind > 0:
            branch_info += f" (behind {status.behind})"
        lines.append(branch_info)
        
        if status.clean:
            lines.append("✅ **Status:** Working tree clean")
        else:
            lines.append("📝 **Status:** Changes detected")
            
            if status.staged:
                lines.append("\n🟢 **Staged changes:**")
                for file in status.staged:
                    lines.append(f"  • {file}")
            
            if status.modified:
                lines.append("\n🟡 **Modified files:**")
                for file in status.modified:
                    lines.append(f"  • {file}")
            
            if status.untracked:
                lines.append("\n🔴 **Untracked files:**")
                for file in status.untracked:
                    lines.append(f"  • {file}")
        
        return '\n'.join(lines)


class GitDiffTool:
    """Show Git diff for changes"""
    
    def execute(self, filepath: str = "", staged: bool = False, directory: str = ".") -> str:
        """Show Git diff"""
        try:
            cmd = ["git", "diff"]
            
            if staged:
                cmd.append("--staged")
            
            if filepath:
                cmd.append(filepath)
            
            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                return f"❌ Git diff failed: {result.stderr}"
            
            if not result.stdout.strip():
                return "ℹ️ No changes to show"
            
            return self._format_diff(result.stdout, filepath, staged)
            
        except subprocess.TimeoutExpired:
            return "❌ Git diff timeout"
        except Exception as e:
            return f"❌ Git diff failed: {e}"
    
    def _format_diff(self, diff_output: str, filepath: str, staged: bool) -> str:
        """Format diff output for display"""
        lines = []
        
        # Header
        diff_type = "staged" if staged else "working tree"
        target = f" for {filepath}" if filepath else ""
        lines.append(f"📋 **Git Diff ({diff_type}){target}:**\n")
        
        # Process diff output
        diff_lines = diff_output.split('\n')
        current_file = ""
        
        for line in diff_lines:
            if line.startswith('diff --git'):
                # New file header
                current_file = line.split()[-1][2:]  # Remove a/ prefix
                lines.append(f"📄 **{current_file}**")
            elif line.startswith('@@'):
                # Hunk header
                lines.append(f"🔍 {line}")
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                lines.append(f"🟢 {line}")
            elif line.startswith('-') and not line.startswith('---'):
                # Removed line
                lines.append(f"🔴 {line}")
            elif line.strip() and not line.startswith('index') and not line.startswith('+++') and not line.startswith('---'):
                # Context line
                lines.append(f"⚪ {line}")
        
        return '\n'.join(lines)


class GitAddTool:
    """Add files to Git staging area"""
    
    def execute(self, filepath: str = ".", directory: str = ".") -> str:
        """Add files to staging area"""
        try:
            result = subprocess.run(
                ["git", "add", filepath],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return f"❌ Git add failed: {result.stderr}"
            
            # Get what was added
            status_result = subprocess.run(
                ["git", "status", "--porcelain", "--staged"],
                cwd=directory,
                capture_output=True,
                text=True
            )
            
            staged_files = []
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    staged_files.append(line[3:])  # Remove status code
            
            if staged_files:
                files_list = '\n'.join(f"  • {f}" for f in staged_files)
                return f"✅ **Added to staging area:**\n{files_list}"
            else:
                return "ℹ️ No changes to add"
            
        except subprocess.TimeoutExpired:
            return "❌ Git add timeout"
        except Exception as e:
            return f"❌ Git add failed: {e}"


class GitCommitTool:
    """Commit changes to Git repository"""
    
    def execute(self, message: str, directory: str = ".") -> str:
        """Commit staged changes"""
        try:
            if not message.strip():
                return "❌ Commit message is required"
            
            # Check if there are staged changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain", "--staged"],
                cwd=directory,
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                return "❌ No staged changes to commit"
            
            # Perform commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return f"❌ Git commit failed: {result.stderr}"
            
            # Extract commit hash from output
            commit_hash = ""
            for line in result.stdout.split('\n'):
                if 'commit' in line.lower() or line.startswith('['):
                    commit_hash = line.strip()
                    break
            
            return f"✅ **Committed successfully**\n{commit_hash}\n\n📝 **Message:** {message}"
            
        except subprocess.TimeoutExpired:
            return "❌ Git commit timeout"
        except Exception as e:
            return f"❌ Git commit failed: {e}"


class GitPushTool:
    """Push commits to remote repository"""

    def execute(self, remote: str = "origin", branch: str = "", directory: str = ".") -> str:
        """Push commits to remote repository"""
        try:
            # Get current branch if not specified
            if not branch:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=directory,
                    capture_output=True,
                    text=True
                )
                branch = branch_result.stdout.strip()

                if not branch:
                    return "❌ Could not determine current branch"

            # Check if there are commits to push
            ahead_result = subprocess.run(
                ["git", "rev-list", "--count", f"{remote}/{branch}..HEAD"],
                cwd=directory,
                capture_output=True,
                text=True
            )

            if ahead_result.returncode == 0:
                ahead_count = int(ahead_result.stdout.strip())
                if ahead_count == 0:
                    return "ℹ️ Already up to date - nothing to push"

            # Perform push
            result = subprocess.run(
                ["git", "push", remote, branch],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return f"❌ Git push failed: {result.stderr}"

            return f"✅ **Pushed successfully**\n📤 **Remote:** {remote}/{branch}\n\n{result.stdout}"

        except subprocess.TimeoutExpired:
            return "❌ Git push timeout (60s)"
        except Exception as e:
            return f"❌ Git push failed: {e}"


class GitPullTool:
    """Pull changes from remote repository"""

    def execute(self, remote: str = "origin", branch: str = "", directory: str = ".") -> str:
        """Pull changes from remote repository"""
        try:
            cmd = ["git", "pull"]

            if remote and branch:
                cmd.extend([remote, branch])
            elif remote:
                cmd.append(remote)

            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return f"❌ Git pull failed: {result.stderr}"

            if "Already up to date" in result.stdout:
                return "ℹ️ Already up to date"

            return f"✅ **Pulled successfully**\n📥 **Changes:**\n\n{result.stdout}"

        except subprocess.TimeoutExpired:
            return "❌ Git pull timeout (60s)"
        except Exception as e:
            return f"❌ Git pull failed: {e}"


class GitLogTool:
    """Show Git commit history"""

    def execute(self, count: int = 10, oneline: bool = True, directory: str = ".") -> str:
        """Show Git commit history"""
        try:
            cmd = ["git", "log", f"-{count}"]

            if oneline:
                cmd.append("--oneline")
            else:
                cmd.extend(["--pretty=format:%h - %an, %ar : %s"])

            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return f"❌ Git log failed: {result.stderr}"

            if not result.stdout.strip():
                return "ℹ️ No commits found"

            lines = [f"📜 **Git History (last {count} commits):**\n"]

            for line in result.stdout.strip().split('\n'):
                if line:
                    lines.append(f"  • {line}")

            return '\n'.join(lines)

        except subprocess.TimeoutExpired:
            return "❌ Git log timeout"
        except Exception as e:
            return f"❌ Git log failed: {e}"


class GitBranchTool:
    """Manage Git branches"""

    def execute(self, action: str = "list", branch_name: str = "", directory: str = ".") -> str:
        """Manage Git branches"""
        try:
            if action == "list":
                return self._list_branches(directory)
            elif action == "create":
                return self._create_branch(branch_name, directory)
            elif action == "switch":
                return self._switch_branch(branch_name, directory)
            elif action == "delete":
                return self._delete_branch(branch_name, directory)
            else:
                return f"❌ Unknown branch action: {action}"

        except Exception as e:
            return f"❌ Git branch operation failed: {e}"

    def _list_branches(self, directory: str) -> str:
        """List all branches"""
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=directory,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"❌ Failed to list branches: {result.stderr}"

        lines = ["🌿 **Git Branches:**\n"]

        for line in result.stdout.strip().split('\n'):
            if line:
                if line.startswith('*'):
                    lines.append(f"  ➤ {line[2:]} (current)")
                else:
                    lines.append(f"  • {line.strip()}")

        return '\n'.join(lines)

    def _create_branch(self, branch_name: str, directory: str) -> str:
        """Create new branch"""
        if not branch_name:
            return "❌ Branch name is required"

        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=directory,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"❌ Failed to create branch: {result.stderr}"

        return f"✅ **Created and switched to branch:** {branch_name}"

    def _switch_branch(self, branch_name: str, directory: str) -> str:
        """Switch to existing branch"""
        if not branch_name:
            return "❌ Branch name is required"

        result = subprocess.run(
            ["git", "checkout", branch_name],
            cwd=directory,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"❌ Failed to switch branch: {result.stderr}"

        return f"✅ **Switched to branch:** {branch_name}"

    def _delete_branch(self, branch_name: str, directory: str) -> str:
        """Delete branch"""
        if not branch_name:
            return "❌ Branch name is required"

        result = subprocess.run(
            ["git", "branch", "-d", branch_name],
            cwd=directory,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"❌ Failed to delete branch: {result.stderr}"

        return f"✅ **Deleted branch:** {branch_name}"
