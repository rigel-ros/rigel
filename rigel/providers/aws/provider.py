import boto3
from botocore.exceptions import ClientError as BotocoreClientError
from python_on_whales.exceptions import DockerException
from rigel.clients import DockerClient
from rigel.exceptions import ClientError, DockerAPIError, RigelError
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers import Provider
from typing import Any, Dict
from .models import AWSProviderModel, AWSProviderOutputModel


LOGGER = get_logger()


class AWSProvider(Provider):

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
        self.model = ModelBuilder(AWSProviderModel).build([], self.raw_data)
        assert isinstance(self.model, AWSProviderModel)

        self.__docker: DockerClient = DockerClient()
        self.__raw_output_model: Dict[str, Any] = {}

    def connect(self) -> None:
        for service in self.model.services:
            if service == 'ecr':
                self.connect_ecr()
            elif service == 'robomaker':
                self.connect_robomaker()
            else:
                raise RigelError(base=f"Unable to connect. Service '{service}' is invalid or not supported.")
        self.providers_data[self.identifier] = ModelBuilder(AWSProviderOutputModel).build([], self.__raw_output_model)

    def disconnect(self) -> None:
        for service in self.model.services:
            if service == 'ecr':
                self.disconnect_ecr()
            elif service == 'robomaker':
                self.disconnect_robomaker()
            else:
                raise RigelError(base=f"Unable to disconnect. Service '{service}' is invalid or not supported.")
        # del self.providers_data[self.identifier]

    #
    # ELASTIC CONTAINER REGISTRY (ECR)
    #

    def connect_ecr(self) -> None:

        if not self.model.ecr_servers:
            raise Exception("No ECR server was declared while using the 'ecr' service")

        try:
            for server in self.model.ecr_servers:
                LOGGER.debug(f"Attempting login with ECR '{server}'")
                self.__docker.login_ecr(
                    aws_access_key_id=self.model.aws_access_key_id,
                    aws_secret_access_key=self.model.aws_secret_access_key,
                    region_name=self.model.region_name,
                    registry=server
                )
                LOGGER.info(f"Logged in with success to ECR '{server}'")
        except DockerException as exception:
            raise DockerAPIError(exception)

    def disconnect_ecr(self) -> None:

        servers = self.model.ecr_servers

        try:
            for server in servers:
                self.__docker.logout(server)
        except DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged out with success from registry '{server}'")

    #
    # ROBOMAKER
    #

    def connect_robomaker(self) -> None:

        LOGGER.debug("Authenticated with Robomaker")

        try:

            # Obtain Robomaker authentication token
            robomaker_client = boto3.client(
                'robomaker',
                aws_access_key_id=self.model.aws_access_key_id,
                aws_secret_access_key=self.model.aws_secret_access_key,
                region_name=self.model.region_name
            )

        except BotocoreClientError as err:
            raise ClientError('AWS', err)

        LOGGER.info('Authenticated with AWS RoboMaker.')

        self.__raw_output_model['robomaker_client'] = robomaker_client

    def disconnect_robomaker(self) -> None:
        pass  # do nothing
