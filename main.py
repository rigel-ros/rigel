import click
import docker
import os
import sys
from pathlib import Path
from rigel.docker import ImageBuilder
from rigel.exceptions import (
    RigelfileAlreadyExistsError,
    RigelError
)
from rigel.files import (
    Renderer,
    RigelfileCreator,
    YAMLDataLoader
)
from rigel.loggers import ErrorLogger, MessageLogger
from rigel.parsers import RigelfileDecoder, RigelfileParser
from rigel.plugins import Plugin
from typing import List


def create_folder(path: str) -> None:
    """
    Create a folder in case it does not exist yet.

    :type path: string
    :param path: Path of the folder to be created.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def create_configuration_parser() -> RigelfileParser:
    """
    Parse information inside local Rigelfile.

    :rtype: rigle.parsers.RigelfileParser
    :return: The parsed information.
    """
    yaml_data = YAMLDataLoader('./Rigelfile').load()
    decoded = RigelfileDecoder().decode(yaml_data)
    return RigelfileParser(decoded)


def create_docker_client() -> docker.api.client.APIClient:
    """
    Create a Docker client intance.

    :rtype docker.api.client.APIClient
    ::return: A docker client instance.
    """
    return docker.from_env().api


def rigelfile_exists() -> bool:
    """
    Verify if a Rigelfile is present.

    :rtype: bool
    :return: True if a Rigelfile is found at the current directory. False otherwise.
    """
    return os.path.isfile('./Rigelfile')


def run_plugins(plugins: List[Plugin]) -> None:
    """
    Run a set of external plugins.

    :rtype plugins: List[rigel.plugin.Plugin]
    :return plugins: List of external plugins to be run.
    """
    try:

        if plugins:
            for plugin in plugins:
                MessageLogger().info(f'Using external plugin {plugin.__class__.__module__}.{plugin.__class__.__name__}')
                plugin.run()
        else:
            MessageLogger().warning('No plugin was declared.')

    except RigelError as err:
        ErrorLogger().log(err)
        sys.exit(err.code)


@click.group()
def cli() -> None:
    """
    Rigel - containerize and deploy your ROS application using Docker
    """
    pass


@click.command()
@click.option('--force', is_flag=True, default=False, help='Write over an existing Rigelfile.',)
def init(force: bool) -> None:
    """
    Create an empty Rigelfile.
    """
    try:

        if rigelfile_exists() and not force:
            raise RigelfileAlreadyExistsError()

        RigelfileCreator().create()
        print('Rigelfile created with success.')

    except RigelfileAlreadyExistsError as err:
        ErrorLogger().log(err)
        sys.exit(err.code)


@click.command()
def create() -> None:
    """
    Create all files required to containerize your ROS application.
    """

    create_folder('.rigel_config')

    try:

        configuration_parser = create_configuration_parser()

        renderer = Renderer(configuration_parser.dockerfile)

        renderer.render('Dockerfile.j2', 'Dockerfile')
        renderer.render('entrypoint.j2', 'entrypoint.sh')
        if configuration_parser.dockerfile.ssh:
            renderer.render('config.j2', 'config')

    except RigelError as err:
        ErrorLogger().log(err)
        sys.exit(err.code)


@click.command()
def build() -> None:
    """
    Build a Docker image with your ROS application.
    """

    configuration_parser = create_configuration_parser()
    docker_client = create_docker_client()

    try:
        builder = ImageBuilder(docker_client)
        builder.build(configuration_parser.dockerfile)

    except RigelError as err:
        ErrorLogger().log(err)
        sys.exit(err.code)


@click.command()
def deploy() -> None:
    """
    Push a Docker image to a remote image registry.
    """
    configuration_parser = create_configuration_parser()
    run_plugins(configuration_parser.registry_plugins)


@click.command()
def run() -> None:
    """
    Start your containerized ROS application.
    """
    configuration_parser = create_configuration_parser()
    run_plugins(configuration_parser.simulation_plugins)


# Add commands to CLI
cli.add_command(init)
cli.add_command(create)
cli.add_command(build)
cli.add_command(deploy)
cli.add_command(run)


def main() -> None:
    """
    Rigel application entry point.
    """
    cli()


if __name__ == '__main__':
    main()
