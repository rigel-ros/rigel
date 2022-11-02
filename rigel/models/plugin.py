from pydantic import BaseModel
from typing import Any, Dict


class PluginSection(BaseModel):
    """A placeholder for information regarding a single plugin.

    Each plugin consists of a Python module installed in the system
    and then loaded at runtime by Rigel.

    Each entrypoint class must be compliant with
    the protocol rigel.plugins.Plugin.

    :type plugin: string
    :cvar plugin: The plugin module to import.
    :type plugin_kwargs: Dict[str, Any]
    :cvar plugin_kwargs: Positional arguments to be passed to the entrypoint class.
    """
    # Required fields.
    plugin: str

    # List of private fields.
    plugin_kwargs: Dict[str, Any] = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        if kwargs.get('with', False):
            kwargs['plugin_kwargs'] = kwargs.pop('with')

        super().__init__(*args, **kwargs)
