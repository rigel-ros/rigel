import click
import os
import sys
from pathlib import Path
from rigelcore.docker import DockerClient
from rigelcore.exceptions import RigelError
from rigelcore.loggers import ErrorLogger, MessageLogger
from rigel.exceptions import RigelfileAlreadyExistsError
from rigel.files import (
    Renderer,
    RigelfileCreator,
    YAMLDataDecoder,
    YAMLDataLoader
)
from rigel.models import ModelBuilder, Rigelfile, PluginSection
from rigel.plugins import PluginInstaller
from typing import Any, Dict, List

from rigel.plugins.loader import PluginLoader


MESSAGE_LOGGER = MessageLogger()


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
    try:

        if plugins:
            for plugin in plugins:

                MESSAGE_LOGGER.warning(f"Loading external plugin '{plugin.name}'.")
                loader = PluginLoader()
                plugin_instance = loader.load(plugin)

                MESSAGE_LOGGER.warning(f"Executing external plugin '{plugin.name}'.")
                plugin_instance.run()

                MESSAGE_LOGGER.info(f"Plugin '{plugin.name}' finished execution with success.")

        else:
            MESSAGE_LOGGER.warning('No plugin was declared.')

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
    try:

        if rigelfile_exists() and not force:
            raise RigelfileAlreadyExistsError()

        rigelfile_creator = RigelfileCreator()
        rigelfile_creator.create()
        MESSAGE_LOGGER.info('Rigelfile created with success.')

    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def create() -> None:
    """
    Create all files required to containerize your ROS application.
    """
    create_folder('.rigel_config')
    try:

        rigelfile = parse_rigelfile()
        renderer = Renderer(rigelfile.build)

        renderer.render('Dockerfile.j2', 'Dockerfile')
        MESSAGE_LOGGER.info("Created file '.rigel_config/Dockerfile'.")

        renderer.render('entrypoint.j2', 'entrypoint.sh')
        MESSAGE_LOGGER.info("Created file '.rigel_config/entrypoint.sh'.")

        if rigelfile.build.ssh:
            renderer.render('config.j2', 'config')
            MESSAGE_LOGGER.info("Created file '.rigel_config/config'.")

    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def build() -> None:
    """
    Build a Docker image with your ROS application.
    """
    rigelfile = parse_rigelfile()
    if rigelfile.build.keys and not rigelfile.build.rosinstall:
        MESSAGE_LOGGER.warning('No .rosinstall file was declared. Recommended to remove unused SSH keys from Dockerfile.')

    buildargs: Dict[str, str] = {}
    for key in rigelfile.build.ssh:
        if not key.file:
            value = os.environ[key.value]  # NOTE: SSHKey model ensures that environment variable is declared.
            buildargs[key.value] = value

    try:
        MESSAGE_LOGGER.info(f"Building Docker image '{rigelfile.build.image}'.")
        builder = DockerClient()
        builder.build('.rigel_config/Dockerfile', rigelfile.build.image, buildargs)
        MESSAGE_LOGGER.info(f"Docker image '{rigelfile.build.image}' built with success.")
    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def deploy() -> None:
    """
    Push a Docker image to a remote image registry.
    """
    MESSAGE_LOGGER.info('Deploying containerized ROS package.')
    rigelfile = parse_rigelfile()
    run_plugins(rigelfile.deploy)


@click.command()
def run() -> None:
    """
    Start your containerized ROS application.
    """
    MESSAGE_LOGGER.info('Starting containerized ROS application.')
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
