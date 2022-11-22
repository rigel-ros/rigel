from pydantic import BaseModel, Field, validator
from rigel.exceptions import UnsupportedPlatformError
from rigel.models.package import Package
from typing import Dict, List, Literal, Optional, Union
from typing_extensions import Annotated


SUPPORTED_PLATFORMS: List[str] = [
    'linux/amd64',
    'linux/arm64',
]


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


CredentialsType = Annotated[Union[StandardContainerRegistry, ElasticContainerRegistry], Field(discriminator='type')]


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
    :type registry: Optional[CredentialsType]
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
    registry: Optional[CredentialsType] = None

    @validator('platforms')
    def validate_platforms(cls, platforms: List[str]) -> List[str]:
        """Ensure that all listed platforms are supported by the current default builder.

        :param platforms: A list of architectures candidates for which to build the Docker image.
        :type platforms: List[str]
        :return: A list of supported architectures for which to build the Docker image.
        :rtype: List[str]
        """
        supported_platforms = [p for p in SUPPORTED_PLATFORMS]
        for platform in platforms:
            if platform not in supported_platforms:
                raise UnsupportedPlatformError(platform)
        return platforms
