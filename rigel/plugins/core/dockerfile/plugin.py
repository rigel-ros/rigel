import os
from pathlib import Path
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers.core import SSHProviderOutputModel
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict
from .models import PluginModel
from .renderer import Renderer

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
        self.raw_data['distro'] = application.distro
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)
        assert isinstance(self.model, PluginModel)

        self.__ssh_keys: SSHProviderOutputModel = None

    def setup(self) -> None:  # noqa
        providers = [provider for _, provider in self.providers_data.items() if isinstance(provider, SSHProviderOutputModel)]
        if len(providers) > 1:
            raise RigelError(base='Multiple SSH key providers were found. Please specify which provider you want to use.')
        elif providers:
            self.__ssh_keys = providers[0]

    def start(self) -> None:

        dir = self.application.dir

        workdir = os.path.abspath(dir).split('/')[-1]

        Path(dir).mkdir(parents=True, exist_ok=True)

        renderer = Renderer(self.application.distro, workdir, self.model, self.__ssh_keys)

        renderer.render('Dockerfile.j2', f'{dir}/Dockerfile')
        LOGGER.info(f"Created file {dir}/Dockerfile")

        renderer.render('entrypoint.j2', f'{dir}/dockerfile_entrypoint.sh')
        LOGGER.info(f"Created file {dir}/entrypoint.sh")

        if self.__ssh_keys:
            renderer.render('config.j2', f'{dir}/dockerfile_config')
            LOGGER.info(f"Created file {dir}/config")
