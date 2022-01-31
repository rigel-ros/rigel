import docker
import os
from argparse import ArgumentParser
from pathlib import Path
from rigel.docker import ImageBuilder
from rigel.files import YAMLDataLoader
from rigel.parsers import ConfigurationFileParser
from rigel.renderers import DockerfileRenderer, EntrypointRenderer, RigelConfigurationRenderer, SSHConfigurationFileRenderer

# Name of the temporary Docker image to be used locally.
TEMPORARY_IMAGE_NAME = 'rigel:temp'


def create_folder(path: str) -> None:
    """
    Create a folder in case it does not exist yet.

    :type path: string
    :param path: Path of the folder to be created.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def create_plugins_folder() -> None:
    """
    Create Rigel plugin folder.
    This folder is always placed at ~/.rigel/plugins and works as a placeholder for external plugins.
    """
    home = os.path.expanduser('~')
    create_folder(f'{home}/.rigel/plugins')


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


def main() -> None:
    """
    Rigel application entry point
    """

    # Ensure all required folders exist beforehand.
    create_plugins_folder()
    create_folder('.rigel_config')

    # Parse CLI arguments.
    cli_parser = ArgumentParser(prog='Rigel', description='Containerize and deploy your ROS application using Docker.')
    cli_parser.add_argument('command', type=str, help='the command to execute')
    cli_args = cli_parser.parse_args()

    # INIT command
    # Create a new Rigelfile at the present location.
    if cli_args.command == 'init':
        RigelConfigurationRenderer.render()
        return

    # Open and parse Rigelfile.
    yaml_data = YAMLDataLoader.load_data('./Rigelfile')
    configuration_parser = ConfigurationFileParser(yaml_data)

    # Initialize a Docker client instance.
    docker_client = create_docker_client()

    # BUILD command
    # Generate Dockerfile and complementary files.
    # Build Docker image.
    if cli_args.command == 'build':

        DockerfileRenderer.render(configuration_parser.dockerfile)
        EntrypointRenderer.render(configuration_parser.dockerfile)
        if configuration_parser.dockerfile.ssh:
            SSHConfigurationFileRenderer.render(configuration_parser.dockerfile)

        build_args = {}
        for key in configuration_parser.dockerfile.ssh:
            if not key.file:
                build_args[key.value] = os.environ.get(key.value)
        ImageBuilder.build(docker_client, TEMPORARY_IMAGE_NAME, build_args)

    # DEPLOY command
    # Deploy the built Docker image to a image repository.
    elif cli_args.command == 'deploy':

        for plugin in configuration_parser.registry_plugins:
            plugin.tag(docker_client, TEMPORARY_IMAGE_NAME)
            plugin.authenticate(docker_client)
            plugin.deploy(docker_client)


if __name__ == '__main__':
    main()
