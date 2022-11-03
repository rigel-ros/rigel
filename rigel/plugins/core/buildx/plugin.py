import os
import python_on_whales.exceptions
from pydantic import BaseModel, validator
from rigel.clients.docker import DockerClient
from rigel.exceptions import (
    DockerAPIError,
    UnsupportedPlatformError,
    RigelError,
)
from rigel.loggers import get_logger
from rigel.models.package import Package, Target
from rigel.plugins import Plugin as PluginBase
from typing import Dict, List, Optional, Tuple
from ..models import Registry

LOGGER = get_logger()

SUPPORTED_PLATFORMS: List[Tuple[str, str, str]] = [
    # (docker_platform_name, qus_argument, qemu_file_name)
    ('linux/amd64', 'x86_64', ''),
    ('linux/arm64', 'arm', 'qemu-arm')
]

BUILDX_BUILDER_NAME = 'rigel-builder'


class PluginModel(BaseModel):
    """A plugin to build Docker images using Docker BuildX.

    :type distro: string
    :cvar distro: The target ROS distro. This field is automatically populated by Rigel.
    :type image: str
    :cvar image: The name for the final Docker image.
    :type load: bool
    :cvar load: Flag to store built image locally. Defaults to False,
    :type package: str
    :cvar package: The target package identifier. This field is automatically populated by Rigel.
    :type platforms: List[str]
    :cvar platforms: A list of architectures for which to build the Docker image.
    :type push: bool
    :cvar push: Flag to store built image in a remote registry.. Defaults to False,
    :type registry: Optional[rigel.files.Registry]
    :cvar registry: Information about the image registry for the Docker image. Default value is None.
    """

    # Required fields.
    distro: str
    image: str
    package: Package

    # Optional fields.
    buildargs: Dict[str, str] = {}
    load: bool = False
    platforms: List[str] = []
    push: bool = False
    registry: Optional[Registry] = None

    @validator('platforms')
    def validate_platforms(cls, platforms: List[str]) -> List[str]:
        """Ensure that all listed platforms are supported by the current default builder.

        :param platforms: A list of architectures candidates for which to build the Docker image.
        :type platforms: List[str]
        :return: A list of supported architectures for which to build the Docker image.
        :rtype: List[str]
        """
        supported_platforms = [p[0] for p in SUPPORTED_PLATFORMS]
        for platform in platforms:
            if platform not in supported_platforms:
                raise UnsupportedPlatformError(platform=platform)
        return platforms


class Plugin(PluginBase):

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)
        self.__docker: DockerClient = DockerClient()

    def login(self, plugin: PluginModel) -> None:
        """Login to a Docker image registry.

        :param plugin: Plugin data.
        :type plugin: PluginModel
        """
        username = plugin.registry.username
        server = plugin.registry.server

        try:
            self.__docker.login(
                username=username,
                password=plugin.registry.password,
                server=server
            )
        except python_on_whales.exceptions.DockerException as exception:
            print(exception)
            raise DockerAPIError(exception=exception)

        LOGGER.info(f"Logged in with success as user '{username}' with registry '{server}'.")

    def logout(self, plugin: PluginModel) -> None:
        """Logout from a Docker image registry.

        :param plugin: Plugin data.
        :type plugin: PluginModel
        """
        server = plugin.registry.server

        try:
            self.__docker.logout(server)
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception=exception)

        LOGGER.info(f"Logged out with success from registry '{server}'.")

    def configure_qemu(self) -> None:
        """ Create the required QEMU configuration files.
        These configuration files support the building of multi-architecture Docker images.
        """

        self.__docker.run_container(
            'qus',
            'aptman/qus',
            command=['-s -- -c -p'],
            privileged=True,
            remove=True,
        )

        LOGGER.info("QEMU configuration files were created.")

    def delete_qemu_files(self) -> None:
        """ Delete required QEMU configuration files.
        """

        self.__docker.run_container(
            'qus',
            'aptman/qus',
            command=['-- -r'],
            privileged=True,
            remove=True,
        )

        LOGGER.info("QEMU configuration files were delete.")

    def create_builder(self) -> None:
        """ Create a dedicated Docker Buildx builder.
        """
        self.__docker.create_builder(BUILDX_BUILDER_NAME, use=True)
        LOGGER.info(f"Create builder '{BUILDX_BUILDER_NAME}'.")

    def remove_builder(self) -> None:
        """ Remove dedicated Docker Buildx builder.
        """
        self.__docker.remove_builder(BUILDX_BUILDER_NAME)
        LOGGER.info(f"Removed builder '{BUILDX_BUILDER_NAME}'.")

    def setup(self) -> None:

        self.__targets = [
            (package, package_data, PluginModel(distro=self.distro, package=package_data, **plugin_data))
            for package, package_data, plugin_data in self.targets]

        self.configure_qemu()
        self.create_builder()

        for _, _, plugin_model in self.__targets:

            if plugin_model.registry:
                self.login(plugin_model)

    def run(self) -> None:

        for package, package_data, plugin_model in self.__targets:

            LOGGER.info(f"Building Docker image '{plugin_model.image}' for package '{package}'.")

            complete_buildargs = plugin_model.buildargs
            for key in package_data.ssh:
                if not key.file:
                    # NOTE: SSHKey model ensures that environment variable is declared.
                    complete_buildargs[key.value] = os.environ[key.value]

            try:

                kwargs = {
                    "file": f'{package_data.dir}/Dockerfile',
                    "tags": plugin_model.image,
                    "load": plugin_model.load,
                    "push": plugin_model.push,
                    "build_args": complete_buildargs
                }

                if plugin_model.platforms:
                    kwargs["platforms"] = plugin_model.platforms

                self.__docker.build(package_data.dir, **kwargs)

                if plugin_model.push:
                    LOGGER.info(f"Docker image '{plugin_model.image}' built and pushed with success.")
                elif plugin_model.load:
                    LOGGER.info(f"Docker image '{plugin_model.image}' built with success.")

            except RigelError as err:
                LOGGER.error(err)
                exit(err.code)

    def stop(self) -> None:

        self.delete_qemu_files()
        self.remove_builder()

        for _, _, plugin_model in self.__targets:

            if plugin_model.registry:
                self.logout(plugin_model)
