import typer
from .dependencies import monitor_dependencies, print_status_report

app = typer.Typer()

@app.command()
def check_deps():
    """Check dependency status"""
    report = monitor_dependencies()
    print_status_report(report) 