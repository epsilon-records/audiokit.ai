from typing import Optional
from pathlib import Path
import asyncio
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from .core.agent import CodeAgent
from .models.task import Task, TaskStatus
from .utils.parser import parse_todo_file

app = typer.Typer(help="AI-powered coding assistant")
console = Console()

@app.command()
def run(
    todo_file: Path = typer.Argument(
        "TODO.txt",
        help="Path to TODO.txt file"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        envvar="AICODER_API_KEY",
        help="API key for AI service"
    ),
    auto_commit: bool = typer.Option(
        False,
        "--commit",
        "-c",
        help="Automatically commit changes"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show changes without applying them"
    )
):
    """Run AI-powered code changes based on TODO.txt file."""
    async def _run():
        try:
            # Parse TODO file
            with console.status("[bold blue]Parsing TODO file..."):
                tasks = parse_todo_file(todo_file)
                
            # Initialize agent
            agent = CodeAgent(api_key)
            
            # Process each task
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                for task in tasks:
                    # Skip completed or deferred tasks
                    if task.status in [TaskStatus.COMPLETED, TaskStatus.DEFERRED]:
                        continue
                        
                    progress.add_task(
                        description=f"Processing: {task.title}",
                        total=None
                    )
                    
                    # Process task
                    task = await agent.process_task(task)
                    
                    # Display results
                    if task.status == TaskStatus.COMPLETED:
                        console.print(f"\n[green]✓ {task.title}")
                        
                        # Show changes
                        table = Table(title="Proposed Changes")
                        table.add_column("File")
                        table.add_column("Changes")
                        
                        for change in task.changes:
                            syntax = Syntax(
                                change.content,
                                "python",
                                theme="monokai",
                                line_numbers=True
                            )
                            table.add_row(change.path, syntax)
                            
                        console.print(table)
                        
                        # Show explanation
                        console.print(Panel(
                            task.metadata["explanation"],
                            title="AI Explanation",
                            border_style="blue"
                        ))
                        
                        # Apply changes if not dry run
                        if not dry_run:
                            with console.status("[bold blue]Applying changes..."):
                                for change in task.changes:
                                    path = Path(change.path)
                                    path.write_text(change.content)
                                    
                                if auto_commit:
                                    # TODO: Implement git commit
                                    pass
                                    
                    else:
                        console.print(f"\n[red]✗ {task.title}")
                        console.print(f"Error: {task.metadata.get('error', 'Unknown error')}")
                        
        except Exception as e:
            console.print(f"[red]Error: {str(e)}")
            raise typer.Exit(1)
            
    asyncio.run(_run())

@app.command()
def init():
    """Initialize a new project with AI-coder."""
    try:
        # Create default TODO.txt
        todo_template = """
        High Priority:
        1. [ ] First task
           Description: Task details here
        
        Medium Priority:
        1. [ ] Another task
           Description: More details
        
        Low Priority:
        1. [ ] Future task
           Description: Future work
        """
        
        Path("TODO.txt").write_text(todo_template.strip())
        console.print("[green]✓ Created TODO.txt")
        
        # Create config file
        config_template = """
        # AI-Coder Configuration
        auto_commit: false
        test_command: "pytest"
        """
        
        Path(".aicoder.yml").write_text(config_template.strip())
        console.print("[green]✓ Created .aicoder.yml")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise typer.Exit(1)

@app.command()
def status():
    """Show current project status."""
    try:
        # Parse TODO file
        tasks = parse_todo_file(Path("TODO.txt"))
        
        # Create status table
        table = Table(title="Project Status")
        table.add_column("Task")
        table.add_column("Status")
        table.add_column("Priority")
        
        for task in tasks:
            status_color = {
                TaskStatus.TODO: "yellow",
                TaskStatus.IN_PROGRESS: "blue",
                TaskStatus.COMPLETED: "green",
                TaskStatus.FAILED: "red",
                TaskStatus.DEFERRED: "grey"
            }.get(task.status, "white")
            
            table.add_row(
                task.title,
                f"[{status_color}]{task.status}[/{status_color}]",
                str(task.priority)
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 