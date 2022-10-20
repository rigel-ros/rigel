import os
import python_on_whales.exceptions
from pydantic import BaseModel, PrivateAttr, validator
from rigel.clients.docker import DockerClient
from rigel.exceptions import (
    DockerAPIError,
    UnsupportedPlatformError,
    RigelError,
)
from rigel.loggers import get_logger
from rigel.models.rigelfile import Package
from typing import Any, Dict, List, Optional, Tuple
from ..models import Registry

LOGGER = get_logger()

SUPPORTED_PLATFORMS: List[Tuple[str, str, str]] = [
    # (docker_platform_name, qus_argument, qemu_file_name)
    ('linux/amd64', 'x86_64', ''),
    ('linux/arm64', 'arm', 'qemu-arm')
]

BUILDX_BUILDER_NAME = 'rigel-builder'


class Plugin(BaseModel):
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
    # Automatically provided fields.
    distro: str
    package: Package

    # Required fields.
    image: str

    # Optional fields.
    buildargs: Dict[str, str] = {}
    load: bool = False
    platforms: List[str] = []
    push: bool = False
    registry: Optional[Registry] = None

    # Private fields.
    _docker: DockerClient = PrivateAttr()

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self._docker = DockerClient()

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

    def get_package_paths(self) -> Tuple[str, str]:
        if self.package.dir:
            return (
                os.path.abspath(f'{self.package.dir}'),                      # package root
                os.path.abspath(f'{self.package.dir}/.rigel_config')         # Dockerfile folder
            )
        else:
            return (
                os.path.abspath(f'.rigel_config/{self.package.name}'),    # package root
                os.path.abspath(f'.rigel_config/{self.package.name}')     # Dockerfile folder
            )

    def login(self) -> None:
        """Login to a Docker image registry.
        """
        username = self.registry.username
        server = self.registry.server

        try:
            self._docker.login(
                username=username,
                password=self.registry.password,
                server=server
            )
        except python_on_whales.exceptions.DockerException as exception:
            print(exception)
            raise DockerAPIError(exception=exception)

        LOGGER.info(f"Logged in with success as user '{username}' with registry '{server}'.")

    def logout(self) -> None:
        """Logout from a Docker image registry.
        """
        server = self.registry.server

        try:
            self._docker.logout(server)
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception=exception)

        LOGGER.info(f"Logged out with success from registry '{server}'.")

    def configure_qemu(self) -> None:
        """ Create the required QEMU configuration files.
        These configuration files support the building of multi-architecture Docker images.
        """

        LOGGER.info("Configuring QEMU.")

        for arch, _, qemu_config_file in SUPPORTED_PLATFORMS:
            if arch in self.platforms:
                if not os.path.exists(f'/proc/sys/fs/binfmt_misc/{qemu_config_file}'):
                    self._docker.run_container(
                        'qus',
                        'aptman/qus',
                        command=['-s -- -c -p'],
                        privileged=True,
                        remove=True,
                    )

        LOGGER.info(f"QEMU configuration files were created for the following architectures {', '.join(self.platforms)}.")

    def create_builder(self) -> None:
        """ Create a dedicated Docker Buildx builder.
        """
        self._docker.create_builder(BUILDX_BUILDER_NAME, use=True)
        LOGGER.info(f"Create builder '{BUILDX_BUILDER_NAME}'.")

    def remove_builder(self) -> None:
        """ Remove dedicated Docker Buildx builder.
        """
        self._docker.remove_builder(BUILDX_BUILDER_NAME)
        LOGGER.info(f"Removed builder '{BUILDX_BUILDER_NAME}'.")

    def setup(self) -> None:
        if self.registry:
            self.login()

        if self.platforms:
            self.configure_qemu()
            self.create_builder()

    def run(self) -> None:
        LOGGER.info(f"Building Docker image '{self.image}'.")

        complete_buildargs = self.buildargs
        for key in self.package.ssh:
            if not key.file:
                # NOTE: SSHKey model ensures that environment variable is declared.
                complete_buildargs[key.value] = os.environ[key.value]

        package_root_path, package_dockerfile_path = self.get_package_paths()

        try:

            kwargs = {
                "file": f'{package_dockerfile_path}/Dockerfile',
                "tags": self.image,
                "load": self.load,
                "push": self.push,
                "build_args": complete_buildargs
            }

            if self.platforms:
                kwargs["platforms"] = self.platforms

            self._docker.build(package_root_path, **kwargs)

            if self.push:
                LOGGER.info(f"Docker image '{self.image}' built and pushed with success.")
            else:
                LOGGER.info(f"Docker image '{self.image}' built with success.")

        except RigelError as err:
            LOGGER.error(err)
            exit(err.code)

    def stop(self) -> None:
        if self.platforms:
            self.remove_builder()

        if self.registry:
            self.logout()
