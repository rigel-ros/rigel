import os
from pathlib import Path
from rigel.clients import DockerClient
from rigel.exceptions import RigelError
from rigel.files import Renderer
from rigel.loggers import get_logger
from rigel.models import DockerSection, DockerfileSection, SUPPORTED_PLATFORMS
from sys import exit
from typing import Dict, Tuple, Union

LOGGER = get_logger()


class ROSPackage:

    @staticmethod
    def generate_paths(package: DockerSection) -> Tuple[str, str]:
        if package.dir:
            return (
                os.path.abspath(f'{package.dir}'),                      # package root
                os.path.abspath(f'{package.dir}/.rigel_config')         # Dockerfile folder
            )
        else:
            return (
                os.path.abspath(f'.rigel_config/{package.package}'),    # package root
                os.path.abspath(f'.rigel_config/{package.package}')     # Dockerfile folder
            )

    @staticmethod
    def build_image(package: DockerfileSection, load: bool, push: bool) -> None:
        """
        Containerize a given Rigel-ROS package (existing Dockerfile).

        :type package: rigel.models.DockerfileSection
        :param package: The Dockerfile to use to containerize.
        :type load: bool
        :param package: Store built image locally.
        :type push: bool
        :param package: Store built image in a remote registry.
        """
        LOGGER.warning(f"Creating Docker image using provided Dockerfile at {package.dockerfile}")

        ROSPackage.login(package)

        path = os.path.abspath(package.dockerfile)

        LOGGER.info(f"Building Docker image {package.image}")
        builder = DockerClient()
        kwargs = {
            "tags": package.image,
            "load": load,
            "push": push
        }
        builder.build(path, **kwargs)

        LOGGER.info(f"Docker image '{package.image}' built with success.")
