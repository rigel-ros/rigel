from pydantic import BaseModel
from typing import Dict, List, Optional


class PluginModel(BaseModel):
    """
    A placeholder for information regarding a containerized ROS package.

    :type image: string
    :param name: The Docker image.
    :type command: Optional[str]
    :param command: The command to be executed inside the container.
    :type environment: Optional[List[str]]
    :param environment: The list of environment variables to set inside the container.
    :type instrospection: List[str].
    :param instrospection: The list of conditions that must be fulfilled.
    :type network: Optional[str]
    :param network: The name of the network to connect the container to.
    :type ports: Optional[Dict[str, Optional[int]]]
    :param ports: The container ports to expose.
    :type volumes: Optional[List[str]]
    :param volumes: The list of volumes to be mounted inside the container.
    """
    # Required fields
    image: str

    # Optional fields
    command: Optional[str] = None
    environment: Optional[List[str]] = []
    introspection: List[str] = []
    network: Optional[str] = None
    ports: Optional[Dict[str, Optional[int]]] = None
    privileged: bool = False
    volumes: Optional[List[str]] = None
