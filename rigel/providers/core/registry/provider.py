from python_on_whales.exceptions import DockerException
from rigel.clients import DockerClient
from rigel.exceptions import DockerAPIError
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers import Provider
from typing import Any, Dict
from .models import ContainerRegistryProviderModel

LOGGER = get_logger()


class ContainerRegistryProvider(Provider):

    def __init__(
        self,
        identifier: str,
        raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any]
    ) -> None:
        super().__init__(
            identifier,
            raw_data,
            global_data,
            providers_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(ContainerRegistryProviderModel).build([], self.raw_data)
        assert isinstance(self.model, ContainerRegistryProviderModel)

        self.__docker: DockerClient = DockerClient()

    def connect(self) -> None:

        server = self.model.server
        username = self.model.username
        LOGGER.debug(f"Attempting login '{username}' with registry '{server}'")

        try:
            self.__docker.login(
                username=username,
                password=self.model.password,
                server=server
            )
        except DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged in with success as user '{username}' with registry '{server}'")

    def disconnect(self) -> None:

        server = self.model.server

        try:
            self.__docker.logout(server)
        except DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged out with success from registry '{server}'")
