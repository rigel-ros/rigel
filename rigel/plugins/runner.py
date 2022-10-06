import signal
from .plugin import Plugin
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from typing import Any, Callable, Optional, Tuple

LOGGER = get_logger()


class PluginRunner:
    """
    A class to run external Rigel plugins at runtime.
    """

    def run(
        self,
        plugin: Tuple[str, Plugin],
        introspection: Optional[Callable] = None
    ) -> None:
        """
        Run an external Rigel plugin.

        :type plugin: Tuple[str, rigel.plugin.Plugin]
        :param plugin: An external plugin to be run.
        :type instrospection: Optional[Callable]
        :param instrospection: A function .
        """
        try:

            plugin_name, plugin_instance = plugin

            def stop_plugin(*args: Any) -> None:
                plugin_instance.stop()
                LOGGER.info(f"Plugin '{plugin_name}' stopped executing gracefully.")
                exit(0)

            signal.signal(signal.SIGINT, stop_plugin)
            signal.signal(signal.SIGTSTP, stop_plugin)

            LOGGER.warning(f"Executing external plugin '{plugin_name}'.")
            plugin_instance.run()

            if introspection:
                introspection()

            plugin_instance.stop()
            LOGGER.info(f"Plugin '{plugin_name}' finished execution with success.")

        except RigelError as err:
            LOGGER.error(err)
            exit(err.code)
