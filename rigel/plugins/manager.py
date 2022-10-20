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
from rigel.models.rigelfile import Package
from typing import Any, Type
from .plugin import Plugin

LOGGER = get_logger()


class PluginManager:

    @staticmethod
    def is_plugin_compliant(entrypoint: Type) -> bool:
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

    @staticmethod
    def is_setup_compliant(entrypoint: Type) -> bool:
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

    @staticmethod
    def is_run_compliant(entrypoint: Type) -> bool:
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

    @staticmethod
    def is_stop_compliant(entrypoint: Type) -> bool:
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

    @staticmethod
    def load(distro: str, package: Package, data: PluginSection) -> Plugin:
        """Parse a list of plugins.

        :type distro: str
        :param distro: The target ROS distro.
        :type package: Package
        :param package: The target package.
        :type plugin: rigel.models.PluginSection
        :param plugin: Information regarding the plugin to load.

        :rtype: Plugin
        :return: An instance of the specified plugin.
        """
        plugin_complete_name = data.plugin.strip()
        plugin_name, plugin_entrypoint = plugin_complete_name.rsplit('.', 1)

        try:
            module = import_module(plugin_name)
            cls: Type = getattr(module, plugin_entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(plugin=plugin_complete_name)

        if not PluginManager.is_plugin_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause="entrypoint class must implement functions 'setup','run', and 'stop'."
            )

        if not PluginManager.is_setup_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.setup' must not receive any parameters."
            )

        if not PluginManager.is_run_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.run' must not receive any parameters."
            )

        if not PluginManager.is_stop_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin_complete_name,
                cause=f"attribute function '{plugin_complete_name}.stop' must not receive any parameters."
            )

        # All plugins are automatically provided with the target ROS distro and the target package.
        data._kwargs['distro'] = distro
        data._kwargs['package'] = package

        return ModelBuilder(cls).build([], data._kwargs)

    @staticmethod
    def run(plugin: Plugin) -> None:
        """Run an external Rigel plugin.

        :type plugin: Tuple[str, rigel.plugin.Plugin]
        :param plugin: A plugin to be run..
        """
        try:

            identifier = plugin.__module__

            def stop_plugin(*args: Any) -> None:
                LOGGER.warning(f"Received signal to stop execution of plugin '{identifier}'")
                plugin.stop()
                LOGGER.debug(f"Plugin '{identifier}' stopped executing gracefully")
                exit(0)

            signal.signal(signal.SIGINT, stop_plugin)
            signal.signal(signal.SIGTSTP, stop_plugin)

            LOGGER.debug(f"Allocating resources for plugin '{identifier}'")
            plugin.setup()

            LOGGER.debug(f"Executing plugin '{identifier}'")
            plugin.run()

            plugin.stop()
            LOGGER.debug(f"Plugin '{identifier}' finished execution with success")

        except RigelError as err:

            LOGGER.error(err)
            exit(err.code)
