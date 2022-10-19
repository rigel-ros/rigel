from pydantic import BaseModel, PrivateAttr
from typing import Any, Dict


class PluginSection(BaseModel):
    """A placeholder for information regarding a single plugin.

    Each plugin consists of a Python module installed in the system
    and then loaded at runtime by Rigel.

    Each entrypoint class must be compliant with
    the protocol rigel.plugins.Plugin.

    :type plugin: string
    :cvar plugin: The plugin module to import.
    :type _kwargs: Dict[str, Any]
    :cvar _kwargs: Positional arguments to be passed to the entrypoint class.
    """
    # Required fields.
    plugin: str

    # List of private fields.
    _kwargs: Dict[str, Any] = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:

        try:
            plugin_name = kwargs['plugin']
            del kwargs['plugin']
        except KeyError:
            raise Exception(msg='Missing plugin name.')

        self._kwargs = kwargs
        super().__init__(name=plugin_name)
