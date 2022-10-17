from pydantic import BaseModel
from typing import List, Dict
from .plugin import PluginSection


class Package(BaseModel):
    """A placeholder for information regarding a single Rigel-ROS package.

    Each Rigel-ROS package may support the execution of individual jobs and job sequences.

    :type jobs: Dict[str, List[PluginSection]]
    :cvar jobs: The jobs supported by the package.
    """
    # Optional fields.
    jobs: Dict[str, List[PluginSection]] = {}


class Workspace(BaseModel):
    """A placeholder for information regarding a single Rigel-ROS workspace.

    Each workspace may contain multiple Rigel-ROS packages and
    support the execution of individual jobs and job sequences.

    :type name: string
    :cvar name: A unique workspace identifier.
    :type distro: string
    :cvar distro: The target ROS distribution of the ROS packages inside the workspace.
    :type jobs: Dict[str, List[PluginSection]]
    :cvar jobs: The jobs supported by the workspace.
    :type packages: List[str]
    :cvar packages: A list of the ROS packages contained within this workspace.
    Each entry corresponds to a path within the workspace 'src' folder.
    """
    # Required fields
    name: str
    distro: str

    # Optional fields
    jobs: Dict[str, List[PluginSection]] = {}
    packages: List[str] = []
