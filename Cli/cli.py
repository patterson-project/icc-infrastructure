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
    "error": "bold red"
})

app = typer.Typer(add_completion=False)
console = Console(theme=icc_cli_theme)


def update_cluster() -> None:
    os.system("sudo kubectl delete --all pods")


@app.command(name="update")
def update() -> None:
    """Updates IoT Control Center with the most recent version."""
    console.print(
        "Deleting all pods and pulling newest from docker hub...", style="info")
    update_cluster()
    console.print("Done.", style="success")
    raise typer.Exit()


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


@app.command(name="database")
def datanase(
    create: bool = typer.Option(False, "--create",
                                "-c", help="Create docker container with MongoDb"),
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
        # ASK for username and password here
        # WARN and ask for confirmation: All exisiting data will be deleted (if exists)
        # Perform a docker compose down and delete all containers in dir
        # docker compose up --build -d
        print("bringing up mongo")
    elif delete:
        # WARN and ask for a confirmation y/n
        # Docker-compose down
        print("deleting mongo")


# Takes options for setting specific
@ app.command(name="variables")
def variables(mongo_ip: bool = typer.Option(False, "--db-ip",
                                            "-dbip", help="Change MongoDb IP address"),
              mongo_username: bool = typer.Option(False, "--db-username",
                                                  "-dbu", help="Change MongoDb admin username"),
              mongo_password: bool = typer.Option(False, "--db-password",
                                                  "-dbp", help="Change MongoDb admin password")) -> None:
    """Set the various environment variables used within the cluster"""
    if mongo_ip:
        print("changing mongo IP")
        # WARN that icc deploy needs to be run for this change to take effect

    if mongo_username:
        print("changing mongodb username")
        # WARN and ask for confirmaion; Make sure device username and password are correct
        # WARN that icc deploy needs to be run for this change to take effect

    if mongo_password:
        print("Changing mongodb password")
        # WARN and ask for y/n; ensure correct password, all connected service connections will fail if wrong
        # WARN that icc deploy needs to be run for this change to take effect

    return


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
