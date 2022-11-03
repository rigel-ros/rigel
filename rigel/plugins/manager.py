import inspect
from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError,
    RigelError
)
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginDataSection
from typing import List, Tuple, Type
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

    def is_setup_compliant(self, entrypoint: Type) -> bool:
        """Ensure that the 'setup' function declared inside a plugin's entrypoint class
        is not expecting any parameters (except for self).

        :type entrypoint: Type
        :param entrypoint: The plugin entrypoint class.

        :rtype: bool
        :return: True is the 'setup' function declared inside a plugin's entrypoint class
        expects no arguments. False otherwise.
        """
        signature = inspect.signature(entrypoint.setup)
        return not len(signature.parameters) != 1  # allows for no parameter besides 'self'

    def is_run_compliant(self, entrypoint: Type) -> bool:
        """Ensure that the 'run' function declared inside a plugin's entrypoint class
        is not expecting any parameters (except for self).

        :type entrypoint: Type
        :param entrypoint: The plugin entrypoint class.

        :rtype: bool
        :return: True if the 'run' function inside the plugin's entrypoint class
        expects no arguments. False otherwise.
        """
        signature = inspect.signature(entrypoint.run)
        return not len(signature.parameters) != 1  # allows for no parameter besides 'self'

    def is_stop_compliant(self, entrypoint: Type) -> bool:
        """Ensure that the 'stop' function declared inside a plugin's entrypoint class
        is not expecting any parameters (except for self).

        :type entrypoint: Type
        :param entrypoint: The plugin entrypoint class.

        :rtype: bool
        :return: True if the 'stop' function inside the plugin's entrypoint class
        expects no arguments. False otherwise.
        """
        signature = inspect.signature(entrypoint.stop)
        return not len(signature.parameters) != 1  # allows for no parameter besides 'self'

    def load(self, entrypoint: str, distro: str, targets: List[Tuple[str, PluginDataSection]]) -> Plugin:
        """Parse a list of plugins.

        :type distro: str
        :param distro: The target ROS distro.
        :type package: Package
        :param package: The target package.
        :type entrypoint: str
        :param entrypoint: The plugin entrypoint.

        :rtype: Plugin
        :return: An instance of the specified plugin.
        """
        plugin_complete_name = entrypoint.strip()
        plugin_name, plugin_entrypoint = plugin_complete_name.rsplit('.', 1)

        try:
            module = import_module(plugin_name)
            cls: Type = getattr(module, plugin_entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(plugin=plugin_complete_name)

        if not self.is_plugin_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause="entrypoint class must implement functions 'setup','run', and 'stop'."
            )

        if not self.is_setup_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.setup' must not receive any parameters."
            )

        if not self.is_run_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.run' must not receive any parameters."
            )

        if not self.is_stop_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.stop' must not receive any parameters."
            )

        return ModelBuilder(cls).build([distro, targets], {})

    def run(self, plugin: Plugin) -> None:
        """Run an external Rigel plugin.

        :type plugin: Tuple[str, rigel.plugin.Plugin]
        :param plugin: A plugin to be run..
        """

        identifier = plugin.__module__

        LOGGER.debug(f"Plugin '{identifier}' started executing.")

        try:
            with plugin:
                plugin.run()
        except RigelError as err:

            LOGGER.warning(f"An error occured during the execution of plugin '{identifier}'")
            LOGGER.warning("Attempting to stop its executing gracefully before handling the error.")
            plugin.stop()

            LOGGER.error(err)
            exit()

        plugin.stop()
        LOGGER.debug(f"Plugin '{identifier}' finished execution with success")
