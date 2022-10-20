from pydantic import BaseModel
from typing import Any, List, Dict
from .plugin import PluginSection


class Package(BaseModel):
    """A placeholder for information regarding a single Rigel-ROS package.

    Each Rigel-ROS package may support the execution of individual jobs.

    :type dir: string
    :cvar dir: The folder containing the ROS package source code, if any.
    :type jobs: Dict[str, List[PluginSection]]
    :cvar jobs: The jobs supported by the package.
    """
    # Required fields.
    name: str

    # Optional fields.
    dir: str = ''
    jobs: Dict[str, List[PluginSection]] = {}


class Rigelfile(BaseModel):
    """A placeholder for information regarding a single Rigel-ROS workspace.

    Each workspace may contain multiple Rigel-ROS packages and
    support the execution of individual jobs and job sequences.

    :type distro: str
    :cvar distro: Target ROS distro.
    :type packages: List[Package]
    :cvar packages: The Rigel-ROS packages contained within this workspace.
    :type sequences: Dict[str, List[str]]
    :cvar sequences: The supported sequence of jobs.
    Each entry corresponds to a path within the workspace 'src' folder.
    :type vars: Dict[str, Any]
    :cvar vars: Section containing the values of global variables.
    """
    # Required fields.
    distro: str

    # Optional fields.
    packages: List[Package] = []
    sequences: Dict[str, List[str]] = {}
    vars: Dict[str, Any] = {}
