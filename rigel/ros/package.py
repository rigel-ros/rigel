import os
from pathlib import Path
from rigel.files import Renderer
from rigel.models import DockerSection, DockerfileSection, SUPPORTED_PLATFORMS
from rigelcore.clients import DockerClient
from rigelcore.exceptions import RigelError
from rigelcore.loggers import get_logger
from sys import exit
from typing import Dict, Tuple

LOGGER = get_logger()


class ROSPackage:

    @staticmethod
    def login(self, package: DockerSection) -> None:
        """
        Login to a Docker image registry.

        :param package: The ROS package to be containerized and deployed.
        :type package: DockerSection
        """
        docker = DockerClient()

        # Authenticate with registry
        if package.registry:

            server = package.registry.server
            username = package.registry.username
            password = package.registry.password

            try:

                LOGGER.info(f'Authenticating with registry {server}')
                docker.login(
                    server=server,
                    username=username,
                    password=password
                )

            except RigelError as err:
                LOGGER.error(err)
                exit(err.code)

    @staticmethod
    def generate_paths(package: DockerSection) -> Tuple[str, str]:
        if package.dir:
            return (
                os.path.abspath(f'{package.dir}'),                      # package root
                os.path.abspath(f'{package.dir}/.rigel_config')         # Dockerfile folder
            )
        else:
            return (
                os.path.abspath(f'.rigel_config/{package.package}'),    # package root
                os.path.abspath(f'.rigel_config/{package.package}')     # Dockerfile folder
            )

    @staticmethod
    def containerize_package(package: DockerSection, load: bool, push: bool) -> None:
        """
        Containerize a given Rigel-ROS package.

        :type package: rigel.models.DockerSection
        :param package: The Rigel-ROS package whose Dockerfile is to be created.
        :type load: bool
        :param package: Store built image locally.
        :type push: bool
        :param package: Store built image in a remote registry.
        """
        LOGGER.info(f"Containerizing package {package.package}.")
        if package.ssh and not package.rosinstall:
            LOGGER.warning('No .rosinstall file was declared. Recommended to remove unused SSH keys from Dockerfile.')

        buildargs: Dict[str, str] = {}
        for key in package.ssh:
            if not key.file:
                value = os.environ[key.value]  # NOTE: SSHKey model ensures that environment variable is declared.
                buildargs[key.value] = value

        path = ROSPackage.generate_paths(package)

        docker = DockerClient()

        ROSPackage.login(package)

        platforms = package.platforms or None

        docker.create_builder('rigel-builder', use=True)
        LOGGER.info("Created builder 'rigel-builder'")

        # Ensure that QEMU is properly configured before building an image.
        for docker_platform, _, qemu_config_file in SUPPORTED_PLATFORMS:
            if not os.path.exists(f'/proc/sys/fs/binfmt_misc/{qemu_config_file}'):
                docker.run_container(
                    'qus',
                    'aptman/qus',
                    command=['-s -- -c -p'],
                    privileged=True,
                    remove=True,
                )
                LOGGER.info(f"Created QEMU configuration file for '{docker_platform}'")

        # Build the Docker image.
        LOGGER.info(f"Building Docker image '{package.image}'")
        try:

            kwargs = {
                "file": f'{path[1]}/Dockerfile',
                "tags": package.image,
                "load": load,
                "push": push
            }

            if buildargs:
                kwargs["build_args"] = buildargs

            if platforms:
                kwargs["platforms"] = platforms

            docker.build(path[0], **kwargs)

            LOGGER.info(f"Docker image '{package.image}' built with success.")
            if push:
                LOGGER.info(f"Docker image '{package.image}' pushed with success.")

        except RigelError as err:
            LOGGER.error(err)
            exit()

        finally:
            # In all situations make sure to remove the builder if existent
            docker.remove_builder('rigel-builder')
            LOGGER.info("Removed builder 'rigel-builder'")

    @staticmethod
    def build_image(package: DockerfileSection, load: bool, push: bool) -> None:
        """
        Containerize a given Rigel-ROS package (existing Dockerfile).

        :type package: rigel.models.DockerfileSection
        :param package: The Dockerfile to use to containerize.
        :type load: bool
        :param package: Store built image locally.
        :type push: bool
        :param package: Store built image in a remote registry.
        """
        LOGGER.warning(f"Creating Docker image using provided Dockerfile at {package.dockerfile}")

        ROSPackage.login(package)

        path = os.path.abspath(package.dockerfile)

        LOGGER.info(f"Building Docker image {package.image}")
        builder = DockerClient()
        kwargs = {
            "tags": package.image,
            "load": load,
            "push": push
        }
        builder.build(path, **kwargs)

        LOGGER.info(f"Docker image '{package.image}' built with success.")

    @staticmethod
    def create_package_files(package: DockerSection) -> None:
        """
        Create all the files required to containerize a given ROS package.

        :type package: rigel.models.DockerSection
        :param package: The ROS package whose Dockerfile is to be created.
        """
        LOGGER.warning(f"Creating build files for package {package.package}.")

        if package.dir:
            path = os.path.abspath(f'{package.dir}/.rigel_config')
        else:
            path = os.path.abspath(f'.rigel_config/{package.package}')

        Path(path).mkdir(parents=True, exist_ok=True)

        renderer = Renderer(package)

        renderer.render('Dockerfile.j2', f'{path}/Dockerfile')
        LOGGER.info(f"Created file {path}/Dockerfile")

        renderer.render('entrypoint.j2', f'{path}/entrypoint.sh')
        LOGGER.info(f"Created file {path}/entrypoint.sh")

        if package.ssh:
            renderer.render('config.j2', f'{path}/config')
            LOGGER.info(f"Created file {path}/config")
