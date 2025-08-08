from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def get_user_input():
    return console.input("[bold green]Ask CodeBuddy > [/bold green]")

def show_output(text):
    console.print(f"[bold cyan]{text}[/bold cyan]")

def show_debug(text):
    """Show debug information in a less intrusive way"""
    console.print(f"[dim yellow]{text}[/dim yellow]")

def show_success(text):
    """Show success messages in green"""
    console.print(f"[bold green]✅ {text}[/bold green]")

def show_error(text):
    """Show error messages in red"""
    console.print(f"[bold red]❌ {text}[/bold red]")

def show_info(text):
    """Show informational messages"""
    console.print(f"[bold blue]ℹ️  {text}[/bold blue]")

def show_results_panel(title, content):
    """Show results in a formatted panel"""
    panel = Panel(
        content,
        title=title,
        title_align="left",
        border_style="cyan"
    )

    console.print(panel)