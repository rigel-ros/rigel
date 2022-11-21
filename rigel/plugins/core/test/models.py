from pydantic import BaseModel
from typing import Dict, List, Optional


class PluginModel(BaseModel):
    """
    A placeholder for information regarding a containerized ROS package.

    :type image: string
    :param name: The Docker image.
    :type command: str
    :param command: The command to be executed inside the container.
    :type environment: List[str]
    :param environment: The list of environment variables to set inside the container.
    :type instrospection: List[str].
    :param instrospection: The list of conditions that must be fulfilled.
    :type network: str
    :param network: The name of the network to connect the container to.
    :type volumes: List[str]
    :param volumes: The list of volumes to be mounted inside the container.
    """
    # Required fields
    image: str

    # Optional fields
    command: List[str] = []
    environment: List[str] = []
    introspection: List[str] = []
    network: str = ''
    privileged: bool = False
    volumes: List[str] = []
