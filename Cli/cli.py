#!/usr/bin/python3
import os
import subprocess
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
    "warning": "bold yellow",
    "error": "bold red"
})

app = typer.Typer(add_completion=False)
console = Console(theme=icc_cli_theme)


@app.command(name="update")
def update(service_name: str = typer.Option("", "--service", "-s", help="Service to be updated. To see options, try 'icc status' to see available services.")) -> None:
    """Updates icc pods with the most recent version."""
    if service_name != "":
        os.system(f"sudo kubectl delete pods -l svc={service_name}")
    else:
        console.print(
            "Deleting all pods and pulling newest from docker hub...", style="info")
        os.system("sudo kubectl delete --all pods")

    console.print("Done.", style="success")
    raise typer.Exit()


@app.command(name="upgrade")
def upgrade() -> None:
    """Upgrades CLI to the most recent version."""
    console.print("Updating CLI...", style="info")
    os.chdir(os.environ["ICC_INFRASTRUCTURE_PATH"])
    os.system("git pull origin main")
    os.chdir("Cli")
    os.system("bash cli_installer.sh")


@app.command(name="deploy")
def deploy(cpu_architecture: str = typer.Option(..., "--arch", "-a", help="Host CPU architecture. Supported architectures include: arm64, amd64"), service_name: str = typer.Option(..., "--service", "-s", help="Service for which to shell into. To see options, try 'icc status' to see available services.")) -> None:
    """Deploys all icc infrastructure"""
    if cpu_architecture == "amd64":
        os.environ["DOCKER_HUB_USERNAME"] = "canadrian72"
    elif cpu_architecture == "arm64":
        os.environ["DOCKER_HUB_USERNAME"] = "julianpatterson"
    else:
        console.print(
            f"Invalid CPU architecture. {cpu_architecture} is not supported.", style="error")
        raise typer.Exit()

    os.system(
        "sudo kubectl delete --all pods,services,deployments,ingress,secrets")

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
def database(
    create: bool = typer.Option(False, "--create",
                                "-c", help="Create docker container with MongoDb. If an instance already exists, this command has no effect."),
    delete: bool = typer.Option(False, "--delete",
                                "-d", help="Delete docker container with MongoDb")
) -> None:
    """Create or delete the icc local MongoDb"""
    mongo_db_path = os.path.join(
        os.environ["ICC_INFRASTRUCTURE_PATH"], "MongoDb")

    if create and delete or not create and not delete:
        console.print(
            "Invalid options. See help for list of possible commands.", style="error")
        raise typer.Exit()

    if create:
        console.print("Creating database...", style="info")
        os.chdir(mongo_db_path)
        os.system("sudo -E docker compose up --build -d")
        console.print("Done.", style="success")
    elif delete:
        console.print(
            "Warning: All existing database information will be lost. Proceed? y/n: ", end="", style="warning")
        confirmation = input()

        if confirmation == "y":
            console.print("Deleting database...", style="info")
            os.chdir(mongo_db_path)
            os.system("sudo -E docker compose rm")
            os.system(
                "sudo rm -rf database && sudo rm -rf init-mongo.js")
            console.print("Done.", style="success")


def env_variable_replace(variable: str, value: str):
    os.system(
        f"sed -i '/{variable}/c\export {variable}={value}' ~/.bashrc"
    )


def set_env_variable(variable: str, value: str):
    os.system(f"echo 'export {variable}={value}' >> ~/.bashrc")


@app.command(name="variables")
def variables(mongo_ip: bool = typer.Option(False, "--db-ip",
                                            "-dbip", help="Change MongoDb IP address"),
              mongo_username: bool = typer.Option(False, "--db-username",
                                                  "-dbu", help="Change MongoDb admin username"),
              mongo_password: bool = typer.Option(False, "--db-password",
                                                  "-dbp", help="Change MongoDb admin password"),
              media_drive_ip: bool = typer.Option(False, "--media-ip",
                                                  "-mip", help="Change Media Drive IP address"),
              media_path: bool = typer.Option(False, "--media-path",
                                              "-mp", help="Change Media Drive IP address"),
              all: bool = typer.Option(False, "--all",
                                       "-a", help="Change all variables"),
              force: bool = typer.Option(False, "--force",
                                         "-f", help="Force without warnings")) -> None:
    """Set the various environment variables used within the cluster"""

    MONGO_DB_IP = "MONGO_DB_IP"
    MONGO_DB_USERNAME = "MONGO_DB_USERNAME"
    MONGO_DB_PASSWORD = "MONGO_DB_PASSWORD"
    MEDIA_DRIVE_IP = "MEDIA_DRIVE_IP"
    MEDIA_PATH = "MEDIA_PATH"

    environment_variables = subprocess.check_output(
        "env", shell=True, executable='/bin/bash', universal_newlines=True)
    env = dict(line.split("=", 1)
               for line in environment_variables.splitlines() if "=" in line)

    if mongo_ip or all:
        confirmation = None
        if not force:
            console.print(
                "Warning: All connected database connections will be disconnected. Proceed? y/n: ", end="", style="warning")
            confirmation = input()

        if confirmation == "y" or force:
            new_ip = input("New MongoDb IP: ")

            if MONGO_DB_IP in env.keys():
                env_variable_replace(MONGO_DB_IP, new_ip)
            else:
                set_env_variable(MONGO_DB_IP, new_ip)

    if mongo_username or all:
        confirmation = None
        if not force:
            console.print(
                "Warning: Changing database username will cause all connected database connections to become unauthenticated. Proceed? y/n: ", end="", style="warning")
            confirmation = input()

        if confirmation == "y" or force:
            new_username = input("New MongoDb admin username: ")

            if MONGO_DB_USERNAME in env.keys():
                env_variable_replace(MONGO_DB_USERNAME, new_username)
            else:
                set_env_variable(MONGO_DB_USERNAME, new_username)

    if mongo_password or all:
        confirmation = None
        if not force:
            console.print(
                "Warning: Changing database password will cause all connected database connections to become unauthenticated. Proceed? y/n: ", end="", style="warning")
            confirmation = input()

        if confirmation == "y" or force:
            new_password = input("New MongoDb admin password: ")

            if MONGO_DB_PASSWORD in env.keys():
                env_variable_replace(MONGO_DB_PASSWORD, new_password)
            else:
                set_env_variable(MONGO_DB_PASSWORD, new_password)

    if media_drive_ip or all:
        new_media_drive_ip = input("New Media Drive IP Address: ")

        if MEDIA_DRIVE_IP in env.keys():
            env_variable_replace(MEDIA_DRIVE_IP, new_media_drive_ip)
        else:
            set_env_variable(MEDIA_DRIVE_IP, new_media_drive_ip)

    if media_path or all:
        new_media_path = input("New Media Drive Path: ")

        if MEDIA_PATH in env.keys():
            env_variable_replace(MEDIA_PATH, new_media_path)
        else:
            set_env_variable(MEDIA_PATH, new_media_path)

    console.print(
        "icc deploy must be run after for changes take effect", style="warning")
    console.print("Done.", style="success")

    return


@ app.command(name="status")
def status(watch: bool = typer.Option(False, "--watch",
                                      "-w", help="Watch pod statuses"),) -> None:
    """Get status of icc Kubernetes pods"""
    if (watch):
        os.system("sudo kubectl get pods -w")
    else:
        os.system("sudo kubectl get pods")


@ app.command(name="logs")
def logs(service_name: str = typer.Option(..., "--service", "-s", help="Service for which logs will be displayed. To see options, try 'icc status' to see available services."),
         follow: bool = typer.Option(False, "--follow",
                                     "-f", help="Follow logs")):
    """Get logs for a service for debugging"""
    follow_flag = ""
    if follow:
        follow_flag = "-f"

    os.system(f"sudo kubectl logs -l svc={service_name} {follow_flag}")


@ app.command(name="shell")
def shell(service_name: str = typer.Option(..., "--service", "-s", help="Service for which to shell into. To see options, try 'icc status' to see available services.")):
    """Start an interactive shell session in the docker container of a service."""
    os.system(
        f"kubectl exec -i -t $(kubectl get pod -l svc={service_name} -o name | sed 's/pods\///') -- bash")


@ app.command(name="discover")
def discover() -> None:
    """List TP-Link Kasa devices on home network"""
    devices = asyncio.run(Discover.discover())
    for address, device in devices.items():
        asyncio.run(device.update())
        print("{:<12} {:<20} {:<20}".format(
            address, device.alias, device.device_type))


@app.command(name="install")
def install() -> None:
    """Installs IoT Control Center on your server"""
    variables(all=True, force=True)
    subprocess.run("source ~/.bashrc")
    database(create=True)
    architecture = input(
        "Enter device CPU architectue (options: amd64, arm64): ")
    deploy(cpu_architecture=architecture)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@ app.callback()
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
