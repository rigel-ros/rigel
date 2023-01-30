from pydantic import BaseModel, Extra
from rigel.loggers import get_logger
from typing import Dict
from .plugin import PluginDataModel


LOGGER = get_logger()


class Application(BaseModel, extra=Extra.forbid):
    """A placeholder for information regarding a single ROS application.
    Each ROS application contains at least one ROS package.

    Each ROS application may support the execution of individual jobs.

    :type distro: str
    :cvar distro: Target ROS distro.
    :type dir: string
    :cvar dir: The folder containing the ROS package source code, if any.
               Defaults to '.'.
    :type jobs: Dict[str, PluginDataModel]
    :cvar jobs: The jobs supported by the package.

    """
    # Required fields.
    distro: str
    jobs: Dict[str, PluginDataModel]

    # Optional fields.
    dir: str = '.'
