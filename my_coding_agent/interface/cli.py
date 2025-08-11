"""
Clean CLI Interface - Beautiful terminal interaction
"""
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table


class CLI:
    """Clean command line interface for the coding agent"""
    
    def __init__(self, agent_name: str = "CodeBuddy"):
        self.console = Console()
        self.agent_name = agent_name
        self.running = False
    
    def start(self, agent):
        """Start the CLI loop"""
        self.running = True
        self._show_welcome()
        
        try:
            while self.running:
                user_input = self._get_user_input()
                
                if not user_input:
                    continue
                
                # Handle system commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self._show_goodbye()
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'clear':
                    self.console.clear()
                    continue
                
                # Process with agent
                self._show_thinking()
                response = agent.process_request(user_input)
                self._show_response(response)
                
        except KeyboardInterrupt:
            self._show_goodbye()
        except Exception as e:
            self.error(f"CLI error: {e}")
    
    def _show_welcome(self):
        """Show welcome message"""
        welcome_text = Text()
        welcome_text.append("🤖 ", style="bold blue")
        welcome_text.append(f"{self.agent_name}", style="bold cyan")
        welcome_text.append(" - Your Intelligent Coding Assistant", style="bold")
        
        panel = Panel(
            welcome_text,
            title="Welcome",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print("💡 Type 'help' for commands, 'exit' to quit\n")
    
    def _show_goodbye(self):
        """Show goodbye message"""
        goodbye = Text("👋 Thanks for using CodeBuddy! Happy coding!", style="bold green")
        self.console.print(Panel(goodbye, border_style="green"))
    
    def _get_user_input(self) -> str:
        """Get user input with nice prompt"""
        try:
            return Prompt.ask(
                "[bold cyan]🤖 CodeBuddy[/bold cyan]",
                default=""
            ).strip()
        except (EOFError, KeyboardInterrupt):
            return "exit"
    
    def _show_thinking(self):
        """Show thinking indicator"""
        self.console.print("🤔 [dim]thinking...[/dim]")
    
    def _show_response(self, response: str):
        """Show agent response with formatting"""
        if response.startswith("❌"):
            self.error(response)
        elif response.startswith("✅"):
            self.success(response)
        elif response.startswith("📄") or response.startswith("📂"):
            self._show_file_content(response)
        else:
            self.info(response)
        
        self.console.print()  # Add spacing
    
    def _show_file_content(self, content: str):
        """Show file content with syntax highlighting"""
        lines = content.split('\n')
        
        # Extract filename from first line if present
        filename = ""
        if lines and "**" in lines[0]:
            import re
            match = re.search(r'\*\*(.*?)\*\*', lines[0])
            if match:
                filename = match.group(1)
        
        # Determine syntax based on file extension
        syntax_lang = "text"
        if filename:
            if filename.endswith('.py'):
                syntax_lang = "python"
            elif filename.endswith('.js'):
                syntax_lang = "javascript"
            elif filename.endswith('.json'):
                syntax_lang = "json"
            elif filename.endswith('.md'):
                syntax_lang = "markdown"
        
        # Show content in a panel
        panel = Panel(
            content,
            title=f"📄 {filename}" if filename else "File Content",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _show_help(self):
        """Show help information"""
        help_text = """
🔧 **Available Commands:**

**File Operations:**
• show me <filename>     - Read and display file
• list files            - Show directory contents
• create <filename>     - Create new file
• delete <filename>     - Delete file (requires approval)

**Folder Operations:**
• create folder <name>  - Create new directory
• delete folder <name>  - Delete directory (requires approval)

**Code Execution:**
• run <filename.py>     - Execute Python file
• run command <cmd>     - Execute shell command (requires approval)
• check syntax <file>   - Check Python syntax

**Git Operations:**
• git status            - Show repository status
• git diff [file]       - Show changes (add --staged for staged changes)
• git add <file>        - Stage files for commit
• git commit <message>  - Commit staged changes
• git push [remote]     - Push commits to remote (requires approval)
• git pull [remote]     - Pull changes from remote
• git log [count]       - Show commit history
• git branch [action]   - Manage branches (list/create/switch/delete)

**Code Analysis:**
• lint <file>           - Check code style and quality
• analyze complexity <file> - Analyze code complexity metrics
• security scan <file>  - Scan for security vulnerabilities
• analyze dependencies  - Check project dependencies
• code quality <file>   - Comprehensive quality analysis

**Code Writing:**
• generate code <description> - Generate code from natural language
• code template <type>  - Generate code templates (python_script, test_file, etc.)
• refactor code <file>  - Refactor and improve existing code
• code snippet <type>   - Generate common code patterns and snippets

**System Commands:**
• help                  - Show this help
• clear                 - Clear screen
• exit/quit            - Exit agent

**Examples:**
• show me main.py
• create calculator.py with basic math functions
• run calculator.py
• git status
• git add main.py
• git commit "Add new feature"
• git push origin main
        """
        
        panel = Panel(
            help_text.strip(),
            title="Help",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def success(self, message: str):
        """Show success message"""
        self.console.print(f"[bold green]{message}[/bold green]")
    
    def error(self, message: str):
        """Show error message"""
        self.console.print(f"[bold red]{message}[/bold red]")
    
    def info(self, message: str):
        """Show info message"""
        self.console.print(f"[cyan]{message}[/cyan]")
    
    def warning(self, message: str):
        """Show warning message"""
        self.console.print(f"[bold yellow]{message}[/bold yellow]")
    
    def ask_approval(self, message: str, risk_level=None, warnings=None, details=None, default: bool = False) -> bool:
        """Ask user for approval with detailed safety information"""
        from safety.approval import RiskLevel

        # Create approval panel based on risk level
        if risk_level == RiskLevel.CRITICAL:
            panel_style = "bold red"
            title = "🚨 CRITICAL OPERATION"
        elif risk_level == RiskLevel.HIGH:
            panel_style = "bold yellow"
            title = "⚠️  HIGH RISK OPERATION"
        elif risk_level == RiskLevel.MEDIUM:
            panel_style = "yellow"
            title = "⚠️  MEDIUM RISK OPERATION"
        else:
            panel_style = "cyan"
            title = "ℹ️  OPERATION APPROVAL"

        # Build approval content
        content = f"**Operation:** {message}\n"

        if warnings:
            content += "\n**Warnings:**\n"
            for warning in warnings:
                content += f"• {warning}\n"

        if details:
            content += "\n**Details:**\n"
            for key, value in details.items():
                content += f"• {key}: {value}\n"

        # Show approval panel
        panel = Panel(
            content.strip(),
            title=title,
            border_style=panel_style,
            padding=(1, 2)
        )

        self.console.print(panel)

        # Handle critical operations
        if risk_level == RiskLevel.CRITICAL:
            self.console.print("\n[bold red]This is a potentially destructive operation![/bold red]")
            confirmation = Prompt.ask(
                "[bold red]Type 'I UNDERSTAND THE RISKS' to proceed[/bold red]",
                default=""
            )
            return confirmation == "I UNDERSTAND THE RISKS"

        # Handle other risk levels
        return Confirm.ask(
            f"[bold]Do you want to proceed with this {risk_level.value if risk_level else 'operation'}?[/bold]",
            default=default
        )

    def show_operation_preview(self, operation: str, details: dict):
        """Show a preview of what an operation will do"""
        table = Table(title=f"Operation Preview: {operation}")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="white")

        for key, value in details.items():
            table.add_row(key, str(value))

        self.console.print(table)
