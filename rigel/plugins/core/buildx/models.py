from pydantic import BaseModel, Extra, validator
from rigel.exceptions import UnsupportedPlatformError
from typing import Dict, List


SUPPORTED_PLATFORMS: List[str] = [
    'linux/amd64',
    'linux/arm64',
]


class PluginModel(BaseModel, extra=Extra.forbid):
    """A plugin to build Docker images using Docker BuildX.

    :type image: str
    :cvar image: The name for the final Docker image.
    :type load: bool
    :cvar load: Flag to store built image locally. Defaults to False,
    :type platforms: List[str]
    :cvar platforms: A list of architectures for which to build the Docker image.
    :type push: bool
    :cvar push: Flag to store built image in a remote registry.. Defaults to False,
    """

    # Required fields.
    image: str

    # Optional fields.
    buildargs: Dict[str, str] = {}
    load: bool = False
    platforms: List[str] = []
    push: bool = False

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
