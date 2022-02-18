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
    YAMLDataDecoder,
    YAMLDataLoader
)
from rigel.loggers import ErrorLogger, MessageLogger
from rigel.models import ModelBuilder, Rigelfile, PluginSection
from rigel.plugins import PluginInstaller
from typing import Any, List

from rigel.plugins.loader import PluginLoader


def handle_rigel_error(err: RigelError) -> None:
    """
    Handler function for errors of type RigelError .
    :type err: RigelError
    :param err: The error to be handled
    """
    error_logger = ErrorLogger()
    error_logger.log(err)
    sys.exit(err.code)


def create_folder(path: str) -> None:
    """
    Create a folder in case it does not exist yet.

    :type path: string
    :param path: Path of the folder to be created.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


# TODO: change return type to Rigelfile
def parse_rigelfile() -> Any:
    """
    Parse information inside local Rigelfile.

    :rtype: rigle.models.Rigelfile
    :return: The parsed information.
    """
    loader = YAMLDataLoader('./Rigelfile')
    decoder = YAMLDataDecoder()

    yaml_data = decoder.decode(loader.load())

    builder = ModelBuilder(Rigelfile)
    return builder.build([], yaml_data)


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


def run_plugins(plugins: List[PluginSection]) -> None:
    """
    Run a set of external plugins.

    :rtype plugins: List[rigel.plugin.Plugin]
    :return plugins: List of external plugins to be run.
    """
    message_logger = MessageLogger()

    try:

        if plugins:
            for plugin in plugins:

                message_logger.info(f"Loading external plugin '{plugin.name}'.")
                loader = PluginLoader()
                plugin_instance = loader.load(plugin)

                message_logger.info(f"Executing external plugin '{plugin.name}'.")
                plugin_instance.run()

                message_logger.info(f"Plugin '{plugin.name}' finished execution with success.")

        else:
            message_logger.warning('No plugin was declared.')

    except RigelError as err:
        handle_rigel_error(err)


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
    message_logger = MessageLogger()

    try:

        if rigelfile_exists() and not force:
            raise RigelfileAlreadyExistsError()

        rigelfile_creator = RigelfileCreator()
        rigelfile_creator.create()
        message_logger.info('Rigelfile created with success.')

    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def create() -> None:
    """
    Create all files required to containerize your ROS application.
    """

    create_folder('.rigel_config')
    message_logger = MessageLogger()

    try:

        rigelfile = parse_rigelfile()
        renderer = Renderer(rigelfile.build)

        renderer.render('Dockerfile.j2', 'Dockerfile')
        message_logger.info("Created file '.rigel_config/Dockerfile'.")

        renderer.render('entrypoint.j2', 'entrypoint.sh')
        message_logger.info("Created file '.rigel_config/entrypoint.sh'.")

        if rigelfile.build.ssh:
            renderer.render('config.j2', 'config')
            message_logger.info("Created file '.rigel_config/config'.")

    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def build() -> None:
    """
    Build a Docker image with your ROS application.
    """
    docker_client = create_docker_client()
    message_logger = MessageLogger()

    rigelfile = parse_rigelfile()
    if rigelfile.build.keys and not rigelfile.build.rosinstall:
        message_logger.warning('No .rosinstall file was declared. Recommended to remove unused SSH keys from Dockerfile.')

    try:
        message_logger.info(f"Building Docker image '{rigelfile.build.image}'.")
        builder = ImageBuilder(docker_client)
        builder.build(rigelfile.build)
        message_logger.info(f"Docker image '{rigelfile.build.image}' built with success.")
    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def deploy() -> None:
    """
    Push a Docker image to a remote image registry.
    """
    message_logger = MessageLogger()
    message_logger.info('Deploying containerized ROS package.')
    rigelfile = parse_rigelfile()
    run_plugins(rigelfile.deploy)


@click.command()
def run() -> None:
    """
    Start your containerized ROS application.
    """
    message_logger = MessageLogger()
    message_logger.info('Starting containerized ROS application.')
    rigelfile = parse_rigelfile()
    run_plugins(rigelfile.simulate)


@click.command()
@click.argument('plugin', type=str)
@click.option('--host', default='github.com', help="URL of the hosting platform. Default is 'github.com'.")
@click.option('--ssh', is_flag=True, default=False, help='Whether the plugin is public or private. Use flag when private.')
def install(plugin: str, host: str, ssh: bool) -> None:
    """
    Install external plugins.
    """
    try:
        installer = PluginInstaller(plugin, host, ssh)
        installer.install()
    except RigelError as err:
        handle_rigel_error(err)


# Add commands to CLI
cli.add_command(init)
cli.add_command(build)
cli.add_command(create)
cli.add_command(deploy)
cli.add_command(install)
cli.add_command(run)


def main() -> None:
    """
    Rigel application entry point.
    """
    cli()


if __name__ == '__main__':
    main()
