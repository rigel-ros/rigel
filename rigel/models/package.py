import python_on_whales.exceptions
import os
from pydantic import BaseModel, Field, PrivateAttr, validator
from rigel.clients import DockerClient
from rigel.exceptions import DockerAPIError, UndeclaredEnvironmentVariableError
from rigel.loggers import get_logger
from typing import Any, Dict, Literal, List, Tuple, Union
from typing_extensions import Annotated
from .plugin import PluginDataSection


LOGGER = get_logger()

Target = Tuple[str, 'Package', PluginDataSection]


class SSHKey(BaseModel):
    """Information placeholder regarding a given private SSH key.

    :type hostname: string
    :cvar hostname: The URL of the host associated with the key.
    :type value: string
    :cvar value: The private SSH key.
    :type file: bool
    :cvar file: Tell if field 'value' consists of a path or a environment variable name. Default is False.
    """

    # NOTE: the validator for field 'value' assumes field 'file' to be already defined.
    # Therefore ensure that field 'file' is always declared before
    # field 'value' in the following list.

    file: bool = False
    hostname: str
    value: str

    @validator('value')
    def ensure_valid_value(cls, v: str, values: Dict[str, Any]) -> str:
        """Ensure that all environment variables have a value.

        :type v: string
        :param v: The value for this SSH key.
        :type values: Dict[str, Any]
        :param values: This model data.
        :rtype: string
        :return: The value for this SSH key.
        """
        if not values['file']:  # ensure value concerns an environment variable
            if not os.environ.get(v):
                raise UndeclaredEnvironmentVariableError(v)
        return v


class StandardContainerRegistry(BaseModel):
    type: Literal['standard']
    server: str
    password: str
    username: str


class ElasticContainerRegistry(BaseModel):
    type: Literal['ecr']
    server: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str


RegistryType = Annotated[Union[StandardContainerRegistry, ElasticContainerRegistry], Field(discriminator='type')]


class Package(BaseModel):
    """A placeholder for information regarding a single ROS package.

    Each ROS package may support the execution of individual jobs.

    :type dir: string
    :cvar dir: The folder containing the ROS package source code, if any. Defaults to '.'.
    :type jobs: Dict[str, PluginDataSection]
    :cvar jobs: The jobs supported by the package.
    :type ssh: List[rigel.files.SSHKey]
    :cvar ssh: A list of all required private SSH keys.
    :type registries: List[RegistryType]
    :cvar registries: A list of image registries to login. Default value is [].
    """
    # Optional fields.
    dir: str = '.'
    jobs: Dict[str, PluginDataSection] = {}
    ssh: List[SSHKey] = []
    registries: List[RegistryType] = []

    # Private fields.
    _docker: str = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._docker: DockerClient = DockerClient()

    def login_registries(self) -> None:
        """
        Login to all image registries.
        """
        for registry in self.registries:
            if isinstance(registry, StandardContainerRegistry):
                self.__login_standard(registry)
            else:  # ElasticContainerRegistry
                self.__login_ecr(registry)

    def __login_standard(self, registry: StandardContainerRegistry) -> None:
        """Login to a standard Docker image registry.

        :param plugin: Standard image registry.
        :type plugin: StandardContainerRegistry
        """
        assert isinstance(registry, StandardContainerRegistry)
        server = registry.server
        username = registry.username
        LOGGER.debug(f"Attempting login '{username}' with registry '{server}'.")
        try:
            self._docker.login(
                username=username,
                password=registry.password,
                server=server
            )
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged in with success as user '{username}' with registry '{server}'.")

    def __login_ecr(self, registry: ElasticContainerRegistry) -> None:
        """Login to a AWS Elastic Container Registry instance.

        :param registry: AWS Elastic Container Registry registry.
        :type registry: ElasticContainerRegistry
        """
        assert isinstance(registry, ElasticContainerRegistry)
        server = registry.server
        LOGGER.debug(f"Attempting login with registry '{server}'.")
        try:
            self._docker.login_ecr(
                aws_access_key_id=registry.aws_access_key_id,
                aws_secret_access_key=registry.aws_secret_access_key,
                region_name=registry.region_name,
                registry=server
            )
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged in with success to {server}.")

    def logout_registries(self) -> None:
        """
        Logout from all image registries.
        """
        for registry in self.registries:
            server = registry.server

            try:
                self._docker.logout(server)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception)

            LOGGER.info(f"Logged out with success from registry '{server}'.")
