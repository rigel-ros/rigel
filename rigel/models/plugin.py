from pydantic import BaseModel, validator
from rigel.exceptions import InvalidPluginNameError
from typing import Any, Dict, List


class PluginSection(BaseModel):
    """
    A placeholder for information regarding a single external plugin.

    Each external plugin consists of an unique Python module that must be
    installed in the system. Plugins are then loaded at runtime by Rigel.

    Each external plugin must contain an entrypoint class responsible for
    plugin setup and execution. Each entrypoint class must be compliant with
    protocol rigel.plugins.Plugin.

    :type name: string
    :cvar name: The name of the plugin module.
    :type args: List[Any]
    :cvar args: List of arguments to be passed to the entrypoint class.
    :type entrypoint: string
    :cvar entrypoint: The name of the class to be instantiated (default Plugin).
    All entrypoint classes must be compliant with protocol rigel.plugins.Plugin .
    :type kwargs: Dict[str, Any]
    :cvar kwargs: Positional arguments to be passed to the entrypoint class.
    """
    # Required fields.
    name: str

    # Optional fields.
    args: List[Any] = []
    entrypoint: str = 'Plugin'
    kwargs: Dict[str, Any] = {}

    @validator('name')
    def validate_name(cls, name: str) -> str:
        """
        Ensure that the plugin name follows the format <AUTHOR>/<PACKAGE>.
        :type name: string
        :param name: Name of the plugin.
        """
        if not len(name.strip().split('/')) == 2:
            raise InvalidPluginNameError(plugin=name)
        return name
