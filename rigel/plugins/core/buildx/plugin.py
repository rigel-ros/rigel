import os
from rigel.clients.docker import DockerClient
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.package import Target
from rigel.plugins import Plugin as PluginBase
from typing import List
from .models import PluginModel


LOGGER = get_logger()

BUILDX_BUILDER_NAME = 'rigel-builder'


class Plugin(PluginBase):

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)
        self.__docker: DockerClient = DockerClient()
        self.prepare_targets()

    def prepare_targets(self) -> None:
        self.__targets = [
            (package_name, package, PluginModel(distro=self.distro, package=package, **plugin_data))
            for package_name, package, plugin_data in self.targets]

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
        self.delete_qemu_files()
        self.configure_qemu()
        self.create_builder()

        for _, package, _ in self.__targets:
            package.login_registries()

    def run(self) -> None:

        for package_name, package, plugin_model in self.__targets:

            LOGGER.info(f"Building Docker image '{plugin_model.image}' for package '{package_name}'.")

            complete_buildargs = plugin_model.buildargs.copy()
            for key in package.ssh:
                if not key.file:
                    # NOTE: SSHKey model ensures that environment variable is declared.
                    complete_buildargs[key.value] = os.environ[key.value]

            try:
                kwargs = {
                    "file": f'{package.dir}/Dockerfile',
                    "tags": plugin_model.image,
                    "load": plugin_model.load,
                    "push": plugin_model.push,
                    "build_args": complete_buildargs
                }

                if plugin_model.platforms:
                    kwargs["platforms"] = plugin_model.platforms

                self.__docker.build(package.dir, **kwargs)

                if plugin_model.push:
                    LOGGER.info(f"Docker image '{plugin_model.image}' built and pushed with success.")
                elif plugin_model.load:
                    LOGGER.info(f"Docker image '{plugin_model.image}' built with success.")

            except RigelError as err:
                LOGGER.error(err)

    def stop(self) -> None:

        self.delete_qemu_files()
        self.remove_builder()

        for _, package, _ in self.__targets:
            package.logout_registries()
