import inspect
import signal
from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError,
    RigelError
)
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginSection
from typing import Any, Tuple, Type
from .plugin import Plugin

LOGGER = get_logger()


class PluginManager:

    def __is_plugin_compliant(self, entrypoint: Type) -> bool:
        """Ensure that a given plugin entrypoint class is compliant with the
        rigel.plugins.Plugin protocol. All compliant plugins must implement
        a 'setup', 'run', and 'stop' functions.

        :type entrypoint: Type
        :param entrypoint: The plugin entrypoint class.

        :rtype: bool
        :return: True if the plugin entrypoint class is compatible with the
        rigle.plugins.Plugin protocol. False otherwise.
        """
        return issubclass(entrypoint, Plugin)

    def __is_setup_compliant(self, entrypoint: Type) -> bool:
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

    def __is_run_compliant(self, entrypoint: Type) -> bool:
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

    def __is_stop_compliant(self, entrypoint: Type) -> bool:
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

    # TODO: set return type to Plugin
    def load(
        self,
        plugin: PluginSection,
    ) -> Any:
        """Parse a list of plugins.

        :type plugin: rigel.models.PluginSection
        :param plugin: Information regarding the plugin to load.

        :rtype: Plugin
        :return: An instance of the specified plugin.
        """
        plugin_complete_name = plugin.name.strip()
        plugin_name, plugin_entrypoint = plugin_complete_name.rsplit('.', 1)

        try:
            module = import_module(plugin_name)
            cls: Type = getattr(module, plugin_entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(plugin=plugin_complete_name)

        if not self.__is_plugin_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause="entrypoint class must implement functions 'setup','run', and 'stop'."
            )

        if not self.__is_setup_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.setup' must not receive any parameters."
            )

        if not self.__is_run_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.run' must not receive any parameters."
            )

        if not self.__is_stop_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.stop' must not receive any parameters."
            )

        builder = ModelBuilder(cls)

        return builder.build([], plugin._kwargs)

    def run(
        self,
        plugin: Tuple[str, Plugin],
    ) -> None:
        """Run an external Rigel plugin.

        :type plugin: Tuple[str, rigel.plugin.Plugin]
        :param plugin: A plugin to be run..
        """
        try:

            plugin_name, plugin_instance = plugin

            def stop_plugin(*args: Any) -> None:
                print()
                LOGGER.warning(f"Received signal to stop execution of plugin '{plugin_name}'")
                plugin_instance.stop()
                LOGGER.info(f"Plugin '{plugin_name}' stopped executing gracefully")
                exit(0)

            signal.signal(signal.SIGINT, stop_plugin)
            signal.signal(signal.SIGTSTP, stop_plugin)

            LOGGER.debug(f"Allocating resources for plugin '{plugin_name}'")
            plugin_instance.setup()

            LOGGER.debug(f"Executing plugin '{plugin_name}'")
            plugin_instance.run()

            plugin_instance.stop()
            LOGGER.info(f"Plugin '{plugin_name}' finished execution with success")

        except RigelError as err:

            LOGGER.error(err)
            exit(err.code)
