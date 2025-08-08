from rich.console import Console

console = Console()

def get_user_input():
    return console.input("[bold green]Ask CodeBuddy > [/bold green]")

def show_output(text):
    console.print(f"[bold cyan]{text}[/bold cyan]")