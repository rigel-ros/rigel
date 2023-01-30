import os
from rigel.clients import DockerClient
from rigel.exceptions import RigelError, UndeclaredEnvironmentVariableError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from rigel.providers.core import SSHProviderOutputModel
from typing import Any, Dict
from .models import PluginModel


LOGGER = get_logger()

BUILDX_BUILDER_NAME = 'rigel-builder'


class Plugin(PluginBase):

    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any]
    ) -> None:
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)
        assert isinstance(self.model, PluginModel)

        self.__docker: DockerClient = DockerClient()

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

    def get_ssh_keys(self) -> None:
        ssh_keys = []
        for _, model in self.providers_data.items():
            if isinstance(model, SSHProviderOutputModel):
                for key in model.keys:
                    if key.env:
                        ssh_keys.append(key)
        return ssh_keys

    def setup(self) -> None:
        self.delete_qemu_files()
        self.configure_qemu()
        self.create_builder()

    def run(self) -> None:

        LOGGER.info(f"Building Docker image '{self.model.image}'.")

        complete_buildargs = self.model.buildargs.copy()
        try:
            for key in self.get_ssh_keys():
                if key.env:
                    complete_buildargs[key.env] = os.environ[key.env]
        except KeyError:
            raise UndeclaredEnvironmentVariableError(env=key.env)

        try:
            kwargs = {
                "file": f'{self.application.dir}/Dockerfile',
                "tags": self.model.image,
                "load": self.model.load,
                "push": self.model.push,
                "build_args": complete_buildargs
            }

            if self.model.platforms:
                kwargs["platforms"] = self.model.platforms

            self.__docker.build(self.application.dir, **kwargs)

            if self.model.push:
                LOGGER.info(f"Docker image '{self.model.image}' built and pushed with success.")
            elif self.model.load:
                LOGGER.info(f"Docker image '{self.model.image}' built with success.")

        except RigelError as err:
            LOGGER.error(err)

    def stop(self) -> None:
        self.delete_qemu_files()
        self.remove_builder()
