import os
import python_on_whales.exceptions
from rigel.clients.docker import DockerClient
from rigel.exceptions import DockerAPIError, RigelError
from rigel.loggers import get_logger
from rigel.models.package import Target
from rigel.plugins import Plugin as PluginBase
from typing import List
from .models import (
    ElasticContainerRegistry,
    StandardContainerRegistry,
    PluginModel
)


LOGGER = get_logger()

BUILDX_BUILDER_NAME = 'rigel-builder'


class Plugin(PluginBase):

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)
        self.__docker: DockerClient = DockerClient()
        self.prepare_targets()

    def prepare_targets(self) -> None:
        self.__targets = [
            (package, package_data, PluginModel(distro=self.distro, package=package_data, **plugin_data))
            for package, package_data, plugin_data in self.targets]

    def login(self, plugin: PluginModel) -> None:
        """Login to a Docker image registry.

        :param plugin: Plugin data.
        :type plugin: PluginModel
        """
        if isinstance(plugin.registry, StandardContainerRegistry):
            self.login_standard(plugin)
        else:  # ElasticContainerRegistry
            self.login_ecr(plugin)

    def login_standard(self, plugin: PluginModel) -> None:
        """Login to a standard Docker image registry.

        :param plugin: Plugin data.
        :type plugin: PluginModel
        """
        assert isinstance(plugin.registry, StandardContainerRegistry)
        server = plugin.registry.server
        username = plugin.registry.username
        LOGGER.debug(f"Attempting login '{username}' with registry '{server}'.")
        try:
            self.__docker.login(
                username=username,
                password=plugin.registry.password,
                server=server
            )
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged in with success as user '{username}' with registry '{server}'.")

    def login_ecr(self, plugin: PluginModel) -> None:
        """Login to a AWS Elastic Container Registry instance.

        :param plugin: Plugin data.
        :type plugin: PluginModel
        """
        assert isinstance(plugin.registry, ElasticContainerRegistry)
        server = plugin.registry.server
        LOGGER.debug(f"Attempting login with registry '{server}'.")
        try:
            self.__docker.login_ecr(
                aws_access_key_id=plugin.registry.aws_access_key_id,
                aws_secret_access_key=plugin.registry.aws_secret_access_key,
                region_name=plugin.registry.region_name,
                registry=server
            )
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged in with success to {server}.")

    def logout(self, plugin: PluginModel) -> None:
        """Logout from a Docker image registry.

        :param plugin: Plugin data.
        :type plugin: PluginModel
        """
        assert plugin.registry
        server = plugin.registry.server

        try:
            self.__docker.logout(server)
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception)

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

        self.configure_qemu()
        self.create_builder()

        for _, _, plugin_model in self.__targets:

            if plugin_model.registry:
                self.login(plugin_model)

    def run(self) -> None:

        for package, package_data, plugin_model in self.__targets:

            LOGGER.info(f"Building Docker image '{plugin_model.image}' for package '{package}'.")

            complete_buildargs = plugin_model.buildargs.copy()
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

    def stop(self) -> None:

        self.delete_qemu_files()
        self.remove_builder()

        for _, _, plugin_model in self.__targets:

            if plugin_model.registry:
                self.logout(plugin_model)
