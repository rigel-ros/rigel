from pydantic import BaseModel
from typing import Any, List, Dict
from .package import Package
from .plugin import PluginSection


class Rigelfile(BaseModel):
    """A placeholder for information regarding a set of ROS packages.

    Each set may contain multiple ROS packages
    supporting the execution of individual jobs and job sequences.

    :type distro: str
    :cvar distro: Target ROS distro.
    :type jobs: Dict[str, PluginSection]
    :cvar jobs: The supported individual jobs.
    :type packages: Dict[str, Package]
    :cvar packages: The set of relevant ROS packages.
    :type sequences: Dict[str, List[str]]
    :cvar sequences: The supported sequence of jobs.
    :type vars: Dict[str, Any]
    :cvar vars: Section containing the values of global variables.
    """
    # Required fields.
    distro: str

    # Optional fields.
    jobs: Dict[str, PluginSection] = {}
    packages: Dict[str, Package] = {}
    sequences: Dict[str, List[str]] = {}
    vars: Dict[str, Any] = {}
