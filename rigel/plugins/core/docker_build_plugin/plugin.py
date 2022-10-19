from pydantic import BaseModel, validator
from rigel.exceptions import UnsupportedPlatformError
from typing import List, Optional, Tuple
from ..models import Registry


SUPPORTED_PLATFORMS: List[Tuple[str, str, str]] = [
    # (docker_platform_name, qus_argument, qemu_file_name)
    ('linux/amd64', 'x86_64', ''),
    ('linux/arm64', 'arm', 'qemu-arm')
]


class Plugin(BaseModel):
    """A plugin to build Docker images using an existing Dockerfile

    :type dockerfile: str
    :cvar dockerfile: The path to a Dockerfile.
    :type image: str
    :cvar image: The name for the final Docker image.
    :type platforms: List[str]
    :cvar platforms: A list of architectures for which to build the Docker image.
    :type registry: Optional[rigel.files.Registry]
    :cvar registry: Information about the image registry for the Docker image. Default value is None.
    """
    # Required fields.
    dockerfile: str
    image: str

    # Optional fields.
    platforms: List[str] = []
    registry: Optional[Registry] = None

    @validator('platforms')
    def validate_platforms(cls, platforms: List[str]) -> List[str]:
        """Ensure that all listed platforms are supported by the current default builder.

        :param platforms: A list of architectures candidates for which to build the Docker image.
        :type platforms: List[str]
        :return: A list of supported architectures for which to build the Docker image.
        :rtype: List[str]
        """
        supported_platforms = [p[0] for p in SUPPORTED_PLATFORMS]
        for platform in platforms:
            if platform not in supported_platforms:
                raise UnsupportedPlatformError(platform=platform)
        return platforms
