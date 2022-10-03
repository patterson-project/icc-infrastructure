#!/usr/bin/python3
import os
from typing import Optional
from rich.console import Console
from rich.theme import Theme
import typer
import asyncio
from kasa import Discover

__version__ = "0.0.1"
__app_name__ = "icc"

icc_cli_theme = Theme({
    "info": "bold cyan",
    "success": "bold green",
    "warning": "magenta",
    "error": "bold red"
})

app = typer.Typer(add_completion=False)
console = Console(theme=icc_cli_theme)


@app.command(name="update")
def update() -> None:
    """Updates IoT Control Center pods with the most recent version."""
    console.print(
        "Deleting all pods and pulling newest from docker hub...", style="info")
    os.system("sudo kubectl delete --all pods")
    console.print("Done.", style="success")
    raise typer.Exit()


@app.command(name="upgrade")
def upgrade() -> None:
    """Upgrades CLI to the most recent version."""
    console.print("Updating CLI...", style="info")
    os.system("git pull origin main")


@app.command(name="deploy")
def deploy(cpu_architecture: str = typer.Option(..., "--arch", "-a", help="Host CPU architecture. Supported architectures include: arm64, amd64")) -> None:
    """Deploys all IoT Control Center infrastructure"""
    if cpu_architecture == "amd64":
        os.environ["DOCKER_HUB_USERNAME"] = "canadrian72"
    elif cpu_architecture == "arm64":
        os.environ["DOCKER_HUB_USERNAME"] = "julianpatterson"
    else:
        console.print(
            f"Invalid CPU architecture. {cpu_architecture} is not supported.", style="error")
        raise typer.Exit()

    os.system("sudo kubectl delete --all pods,services,deployments,ingress,secrets")

    kubernetes_path = os.path.join(
        os.environ["ICC_INFRASTRUCTURE_PATH"], "Kubernetes")

    deployments_path = os.path.join(kubernetes_path, "Deployments")
    for deployment in os.listdir(deployments_path):
        os.chdir(deployments_path)
        os.system(f"envsubst < {deployment} | sudo kubectl apply -f -")

    ingress_path = os.path.join(kubernetes_path, "Ingress")
    for ingress in os.listdir(ingress_path):
        os.chdir(ingress_path)
        os.system(f"envsubst < {ingress} | sudo kubectl apply -f -")

    secrets_path = os.path.join(kubernetes_path, "Secrets")
    for secret in os.listdir(secrets_path):
        os.chdir(secrets_path)
        os.system(f"envsubst < {secret} | sudo kubectl apply -f -")

    console.print("Done.", style="success")


@app.command(name="database")
def datanase(
    create: bool = typer.Option(False, "--create",
                                "-c", help="Create docker container with MongoDb. If an instance already exists, this command has no effect."),
    delete: bool = typer.Option(False, "--delete",
                                "-d", help="Delete docker container with MongoDb")
) -> None:
    """Create or delete the IoT Control Center local MongoDb"""
    mongo_db_path = os.path.join(
        os.environ["ICC_INFRASTRUCTURE_PATH"], "MongoDb")

    if create and delete or not create and not delete:
        console.print(
            "Invalid options. See help for list of possible commands.", style="error")
        raise typer.Exit()

    if create:
        console.print("Creating database...", style="info")
        os.chdir(mongo_db_path)
        os.system("sudo docker compose up --build -d")
        console.print("Done.", style="success")
    elif delete:
        console.print(
            "Warning: All existing database information will be lost. Proceed? y/n: ", end="", style="warning")
        confirmation = input()

        if confirmation == "y":
            console.print("Deleting database...", style="info")
            os.chdir(mongo_db_path)
            os.system("sudo docker compose rm -s -v")
            console.print("Done.", style="success")


@app.command(name="variables")
def variables(mongo_ip: bool = typer.Option(False, "--db-ip",
                                            "-dbip", help="Change MongoDb IP address"),
              mongo_username: bool = typer.Option(False, "--db-username",
                                                  "-dbu", help="Change MongoDb admin username"),
              mongo_password: bool = typer.Option(False, "--db-password",
                                                  "-dbp", help="Change MongoDb admin password")) -> None:
    """Set the various environment variables used within the cluster"""
    if mongo_ip:
        console.print(
            "Warning: All connected database connections will no longer be connected. Proceed? y/n: ", end="", style="warning")
        confirmation = input()

        if confirmation == "y":
            new_ip = input("New MongoDb IP: ")
            os.system(
                f"sudo grep -q \" ^ export MONGO_DB_IP=\" ~/.bashrc && sudo sed \"s | ^export MONGO_DB_IP=.* | MONGO_DB_IP={new_ip} | \" -i ~/.bashrc || sudo sed \"$ a\export MONGO_DB_IP={new_ip}\" -i ~/.bashrc")
            console.print(
                "icc deploy must be run after for changes take effect", style="warning")
            console.print("Done.", style="success")

    if mongo_username:
        console.print(
            "Warning: All connected database connections will be unauthenticated. Proceed? y/n: ", end="", style="warning")
        confirmation = input()

        if confirmation == "y":
            new_username = input("New MongoDb admin username: ")
            os.system(
                f"sudo grep -q \" ^ export MONGO_DB_USERNAME=\" ~/.bashrc && sudo sed \"s | ^export MONGO_DB_USERNAME=.* | MONGO_DB_USERNAME={new_username} | \" -i ~/.bashrc || sudo sed \"$ a\export MONGO_DB_USERNAME={new_username}\" -i ~/.bashrc")
            console.print(
                "icc deploy must be run after for changes to take effect", style="warning")
            console.print("Done.", style="success")

    if mongo_password:
        console.print(
            "Warning: All connected database connections will be unauthenticated. Proceed? y/n: ", end="", style="warning")
        confirmation = input()

        if confirmation == "y":
            new_password = input("New MongoDb admin password: ")
            os.system(
                f"sudo grep -q \" ^ export MONGO_DB_PASSWORD=\" ~/.bashrc && sudo sed \"s | ^export MONGO_DB_PASSWORD=.* | MONGO_DB_PASSWORD={new_password} | \" -i ~/.bashrc || sudo sed \"$ a\export MONGO_DB_PASSWORD={new_password}\" -i ~/.bashrc")
            console.print(
                "icc deploy must be run after for changes to take effect", style="warning")
            console.print("Done.", style="success")

    return


@app.command(name="discover")
def discover() -> None:
    """List TP-Link Kasa devices on home network"""
    devices = asyncio.run(Discover.discover())
    for addr, dev in devices.items():
        asyncio.run(dev.update())
        print(f"{addr} >> {dev}")


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
