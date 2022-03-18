import inspect
from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError,
)
from rigelcore.models import ModelBuilder
from rigel.models import PluginSection
from .plugin import Plugin
from typing import Any, Type


class PluginLoader:
    """
    A class to load external Rigel plugins at runtime.
    """

    def is_plugin_compliant(self, entrypoint: Type) -> bool:
        """
        Ensure that a given plugin entrypoint class is compliant with the
        rigel.plugins.Plugin protocol. All compliant entrypoint classes have
        a 'run' and 'stop' functions.

        :type entrypoint: Type
        :param entrypoint: The external plugin entrypoint class.

        :rtype: bool
        :return: True if the external plugin entrypoint class is compatible with the
        rigle.plugins.Plugin protocol. False otherwise.
        """
        return issubclass(entrypoint, Plugin)

    def is_run_compliant(self, entrypoint: Type) -> bool:
        """
        Ensure that the 'run' function declared inside an external plugin's entrypoint class
        is not expecting any parameters (except for self).

        :type entrypoint: Type
        :param entrypoint: The external plugin entrypoint class.

        :rtype: bool
        :return: True if the 'run' function inside the external plugin's entrypoint class
        exoects no arguments. False otherwise.
        """
        signature = inspect.signature(entrypoint.run)
        return not len(signature.parameters) != 1  # allows for no parameter besides self

    def is_stop_compliant(self, entrypoint: Type) -> bool:
        """
        Ensure that the 'stop' function declared inside an external plugin's entrypoint class
        is not expecting any parameters (except for self).

        :type entrypoint: Type
        :param entrypoint: The external plugin entrypoint class.

        :rtype: bool
        :return: True if the 'stop' function inside the external plugin's entrypoint class
        exoects no arguments. False otherwise.
        """
        signature = inspect.signature(entrypoint.stop)
        return not len(signature.parameters) != 1  # allows for no parameter besides self

    # TODO: set return type to Plugin
    def load(self, plugin: PluginSection) -> Any:
        """
        Parse a list of plugins.

        :type plugin: rigel.models.PluginSection
        :param plugin: Information regarding the plugin to load.

        :rtype: Plugin
        :return: An instance of the specified plugin.
        """
        _, plugin_name = plugin.name.strip().split('/')
        complete_plugin_name = f'{plugin.name}.{plugin.entrypoint}'

        try:
            module = import_module(plugin_name)
            entrypoint = plugin.entrypoint
            cls: Type = getattr(module, entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(plugin=complete_plugin_name)

        if not self.is_plugin_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin.name,
                cause="entrypoint class must implement functions 'run' and 'stop'."
            )

        if not self.is_run_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin.name,
                cause=f"attribute function '{complete_plugin_name}.run' must not receive any parameters."
            )

        if not self.is_stop_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin.name,
                cause=f"attribute function '{complete_plugin_name}.stop' must not receive any parameters."
            )

        builder = ModelBuilder(cls)
        return builder.build(plugin.args, plugin.kwargs)
