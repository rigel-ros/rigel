from pydantic import BaseModel
from typing import Any, Dict, List, Union

PluginDataSection = Dict[str, Any]


class PluginSection(BaseModel):
    """A placeholder for information regarding a single plugin.

    Each plugin consists of a Python module installed in the system
    and then loaded at runtime by Rigel.

    :type plugin: string
    :cvar plugin: The Python module to import.
    :type target: Union[List[str], str]
    :cvar target: The target ROS packages.
    """
    # Required fields.
    plugin: str

    # Optional fields.
    targets: Union[List[str], str] = 'all'
