import click
import docker
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from rigel.docker import ImageBuilder
from rigel.exceptions import (
    RigelfileAlreadyExistsError,
    RigelError
)
from rigel.files import YAMLDataLoader
from rigel.parsers import RigelfileParser
from rigel.renderers import (
    DockerfileRenderer,
    EntrypointRenderer,
    RigelConfigurationRenderer,
    SSHConfigurationFileRenderer
)

# Name of the temporary Docker image to be used locally.
TEMPORARY_IMAGE_NAME = 'rigel:temp'


def create_folder(path: str) -> None:
    """
    Create a folder in case it does not exist yet.

    :type path: string
    :param path: Path of the folder to be created.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def create_docker_client() -> docker.api.client.APIClient:
    """
    Create a Docker client instance.

    :rtype: docker.api.client.APIClient
    :return: A Docker client instance.
    """
    docker_host = os.environ.get('DOCKER_PATH')
    if docker_host:
        return docker.APIClient(base_url=docker_host)
    else:
        return docker.APIClient(base_url='unix:///var/run/docker.sock')

def create_configuration_parser() -> RigelfileParser:
    """
    Parse information inside local Rigelfile.

    :rtype: rigle.parsers.RigelfileParser
    :return: The parsed information.
    """
    yaml_data = YAMLDataLoader.load_data('./Rigelfile')
    return RigelfileParser(yaml_data)

def rigelfile_exists() -> bool:
    """
    Verify if a Rigelfile is present.

    :rtype: bool
    :return: True if a Rigelfile is found at the current directory. False otherwise. 
    """
    return os.path.isfile('./Rigelfile')

@click.group()
def cli():
    """
    Rigel - containerize and deploy your ROS application using Docker
    """
    pass

@click.command()
@click.option('--new', is_flag=True, default=False, help='Write over an existing Rigelfile',)
def init(new) -> None:
    """
    Create an empty Rigelfile.
    """
    try:

        if rigelfile_exists() and not new:
            raise RigelfileAlreadyExistsError()

        create_folder('.rigel_config')
        RigelConfigurationRenderer.render()
        print('Rigelfile created with success.')

    except RigelfileAlreadyExistsError as err:
        print(err)
        sys.exit(err.code)

@click.command()
def build() -> None:
    """
    Build a Docker image encapsulating your ROS application.
    """
    try:

        configuration_parser = create_configuration_parser()
        docker_client = create_docker_client()

        DockerfileRenderer.render(configuration_parser.dockerfile)
        EntrypointRenderer.render(configuration_parser.dockerfile)
        if configuration_parser.dockerfile.ssh:
            SSHConfigurationFileRenderer.render(configuration_parser.dockerfile)

        build_args = {}
        for key in configuration_parser.dockerfile.ssh:
                build_args[key.value] = os.environ.get(key.value)
        ImageBuilder.build(docker_client, TEMPORARY_IMAGE_NAME, build_args)

    except RigelError as err:
        print(err)
        sys.exit(err.code)

@click.command()
def deploy() -> None:
    """
    Push a Docker image to a remote image registry.
    """
    configuration_parser = create_configuration_parser()
    docker_client = create_docker_client()

    if configuration_parser.registry_plugins:
        for plugin in configuration_parser.registry_plugins:
            plugin.tag(docker_client, TEMPORARY_IMAGE_NAME)
            plugin.authenticate(docker_client)
            plugin.deploy(docker_client)
    else:
        print('WARNING - no plugin was declared.')

cli.add_command(init)
cli.add_command(build)
cli.add_command(deploy)

def main() -> None:
    cli()

if __name__ == '__main__':
    main()