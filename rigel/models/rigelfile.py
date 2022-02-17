from pydantic import BaseModel
from typing import Any, Dict, List
from .docker import DockerSection
from .plugin import PluginSection


class Rigelfile(BaseModel):
    """
    Main information placeholder.
    Placeholder for all the information contained within a Rigelfile.
    Each Rigelfile contains the complete information used by Rigel to containerize ROS applications.
    If applicable, information regarding the deployment of Docker images and
    the execution of containerized ROS applications may also also be declared within a Rigelfile.

    Each Rigelfile is divided into several sections.

    :type build: DockerSection
    :cvar build: Section containing information regarding how to containerize a ROS package using Docker.
    :type deploy: List[PluginSection]
    :cvar deploy: Section containing information regarding which external plugins to use when
    deploying Docker images of containerized ROS packages.
    :type simulate: List[PluginSection]
    :cvar simulate: Section containing information regarding which external plugins to use when
    executing the containerized ROS application.
    :type vars: Dict[str, Any]
    :cvar vars: Section containing the values of user-defined global variables.
    """
    # Required sections.
    build: DockerSection

    # Optional sections.
    deploy: List[PluginSection] = []
    simulate: List[PluginSection] = []
    vars: Dict[str, Any] = {}
