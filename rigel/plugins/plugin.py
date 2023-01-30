from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict

LOGGER = get_logger()


class Plugin:
    """This class specifies the interface that all plugins must comply with.
    """

    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
    ) -> None:
        self.raw_data = raw_data
        self.global_data = global_data
        self.application = application
        self.providers_data = providers_data

    def setup(self) -> None:
        """Use this function to allocate plugin resoures.
        """
        pass

    def run(self) -> None:
        """Use this function as an entry point for your plugin.
        """
        pass

    def stop(self) -> None:
        """Use this function to gracefully clean plugin resources.
        """
        pass
