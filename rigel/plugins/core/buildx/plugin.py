import os
import random
import string
from rigel.clients import DockerClient
from rigel.exceptions import RigelError, UndeclaredEnvironmentVariableError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from rigel.providers.core import SSHProviderOutputModel
from typing import Any, Dict, List
from .models import PluginModel


LOGGER = get_logger()


class Plugin(PluginBase):

    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any] = {}  # noqa
    ) -> None:
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)
        assert isinstance(self.model, PluginModel)

        self.__docker: DockerClient = DockerClient()
        self.__builder_id = f"rigel-builder-{self.__builder_id_generator()}"

    # Extracted and adapted from:
    # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    def __builder_id_generator(self, size=16, chars=string.ascii_uppercase + string.digits) -> str:
        return ''.join(random.choice(chars) for _ in range(size))

    def configure_qemu(self) -> None:
        """ Create the required QEMU configuration files.
        These configuration files support the building of multi-architecture Docker images.
        """

        try:
            self.__docker.run_container(
                'qus',
                'aptman/qus',
                command=['-s -- -c -p'],
                privileged=True,
                remove=True,
            )
        except Exception:
            # LOGGER.error('Ignoring error')
            pass  # TODO: improve QEMU configuration mechanism

        LOGGER.info("QEMU configuration files were created.")

    def delete_qemu_files(self) -> None:
        """ Delete required QEMU configuration files.
        """

        try:
            self.__docker.run_container(
                'qus',
                'aptman/qus',
                command=['-- -r'],
                privileged=True,
                remove=True,
            )
        except Exception:
            # LOGGER.error('Ignoring error')
            pass  # TODO: improve QEMU removal mechanism

        LOGGER.info("QEMU configuration files were delete.")

    def create_builder(self) -> None:
        """ Create a dedicated Docker Buildx builder.
        """
        self.__docker.create_builder(self.__builder_id, use=True)
        LOGGER.info(f"Create builder '{self.__builder_id}'.")

    def remove_builder(self) -> None:
        """ Remove dedicated Docker Buildx builder.
        """
        self.__docker.remove_builder(self.__builder_id)
        LOGGER.info(f"Removed builder '{self.__builder_id}'.")

    def get_ssh_keys(self) -> None:
        ssh_keys = []
        for _, model in self.providers_data.items():
            if isinstance(model, SSHProviderOutputModel):
                for key in model.keys:
                    if key.env:
                        ssh_keys.append(key)
        return ssh_keys

    def prepare_image_name(self) -> List[str]:

        name_parts = self.model.image.rsplit(':', 1)
        if not name_parts or '' in name_parts:
            raise RigelError(base=f"Invalid image name was provided '{self.model.image}'")

        tags = set(self.model.tags)

        # Ensure 'latest' tag is always present when required
        if 'latest' not in tags and self.model.force_tag_latest:
            tags.add('latest')
        if 'latest' in tags and not self.model.force_tag_latest:
            tags.remove('latest')

        if len(name_parts) > 1:  # a tag was declared alongside the image name

            LOGGER.debug("Consider using the field 'tags' to define desired image tags")
            tag = name_parts[-1]
            if tag not in tags:
                tags.add(tag)
            return [f"{''.join(name_parts[:-1])}:{_tag}" for _tag in list(tags)]

        else:  # no tag was declared alongside the image name

            if not self.model.force_tag_latest:
                raise RigelError(base=f"Image name '{self.model.image}' was declared without a tag")
            return [f"{name_parts[0]}:{_tag}" for _tag in list(tags)]

    def setup(self) -> None:  # noqa
        # self.delete_qemu_files()
        self.configure_qemu()
        self.create_builder()

    def export_keys(self, buildargs: Dict[str, Any]) -> None:
        try:
            for key in self.get_ssh_keys():
                if key.env:
                    buildargs[key.env] = os.environ[key.env]
        except KeyError:
            raise UndeclaredEnvironmentVariableError(env=key.env)

    def start(self) -> None:

        LOGGER.info(f"Building Docker image '{self.model.image}'.")

        complete_buildargs = self.model.buildargs.copy()
        self.export_keys(complete_buildargs)

        tags = self.prepare_image_name()

        try:
            kwargs = {
                "build_args": complete_buildargs,
                "cache": True,
                "file": f'{self.application.dir}/Dockerfile',
                "load": self.model.load,
                "push": self.model.push,
                "tags": tags
            }

            if self.model.platforms:
                kwargs["platforms"] = self.model.platforms

            self.__docker.build(self.application.dir, **kwargs)

            if self.model.push:
                LOGGER.info("The following Docker images were built and pushed with success:")
                for tag in tags:
                    print(f'- {tag}')

            elif self.model.load:
                LOGGER.info("The following Docker images were built with success:")
                for tag in tags:
                    print(f'- {tag}')

        except RigelError as err:
            LOGGER.error(err)

    def stop(self) -> None:
        self.delete_qemu_files()
        self.remove_builder()
