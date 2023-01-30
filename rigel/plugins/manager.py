from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError
)
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict, Type
from .plugin import Plugin

LOGGER = get_logger()


class PluginManager:

    def is_plugin_compliant(self, entrypoint: Type) -> bool:
        """Ensure that a given plugin entrypoint class is an instance of
        rigel.plugins.Plugin.

        :type entrypoint: Type
        :param entrypoint: The plugin entrypoint class.

        :rtype: bool
        :return: True if the plugin entrypoint class is an instance of
        rigel.plugins.Plugin. False otherwise.
        """
        return issubclass(entrypoint, Plugin)

    def load(
        self,
        entrypoint: str,
        plugin_raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any]
    ) -> Plugin:
        """Parse a list of plugins.

        :type entrypoint: str
        :param entrypoint: The plugin entrypoint.
        :type plugin_raw_data: PluginRawData
        :param plugin_raw_data: The unprocessed plugin configuration data.
        :type global_data: RigelfileGlobalData
        :param global_data: The global data.
        :type application: Application
        :param application: The ROS application.
        :type providers_data: Dict[str, Any]
        :param providers_data: Dynamic data bank for providers.

        :rtype: Plugin
        :return: An instance of the specified plugin.
        """
        plugin_complete_name = entrypoint.strip()
        plugin_name, plugin_entrypoint = plugin_complete_name.rsplit('.', 1)

        try:
            module = import_module(plugin_name)
            cls: Type = getattr(module, plugin_entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(plugin_complete_name)

        if not self.is_plugin_compliant(cls):
            raise PluginNotCompliantError(
                plugin_complete_name,
                "entrypoint class must inherit functions 'setup','run', and 'stop' from class 'Plugin'."
            )

        plugin = ModelBuilder(cls).build([
            plugin_raw_data,
            global_data,
            application,
            providers_data
        ], {})
        assert isinstance(plugin, Plugin)

        return plugin
