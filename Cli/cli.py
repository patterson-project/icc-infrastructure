#!/usr/bin/python3
import os
from typing import Optional
from rich.console import Console
from rich.theme import Theme
import typer

__version__ = "0.0.1"
__app_name__ = "icc"

icc_cli_theme = Theme({
    "info": "bold cyan",
    "success": "bold green",
    "warning": "magenta",
    "danger": "bold red"
})

app = typer.Typer(add_completion=False)
console = Console(theme=icc_cli_theme)

def update_cluster() -> None:
    os.system("sudo kubectl delete --all pods")

@app.command(name="update")
def update() -> None:
    """Updates IoT Control Center with the most recent version."""
    console.print("Deleting all pods and pulling newest from docker hub...", style="info")
    update_cluster()
    console.print("Done.", style="success")
    raise typer.Exit()

@app.command(name="deploy")
def scaffold() -> None:
    """Deploys all IoT infrastructure"""
    icc_infrastructure_path = os.environ["ICC_INFRASTRUCTURE_PATH"]
    print(os.listdir(icc_infrastructure_path))


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

app(prog_name=__app_name__)