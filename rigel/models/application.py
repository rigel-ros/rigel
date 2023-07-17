from pydantic import BaseModel, Extra
from rigel.loggers import get_logger


LOGGER = get_logger()


class Application(BaseModel, extra=Extra.forbid):
    """A placeholder for generic information about a ROS application.
    Each ROS application contains at least one ROS package.

    Each ROS application may support the execution of individual jobs.

    :type distro: str
    :cvar distro: Target ROS distro.
    :type dir: string
    :cvar dir: The folder containing the ROS package source code, if any.
               Defaults to '.'.

    """
    # Required fields.
    distro: str

    # Optional fields.
    dir: str = '.'
