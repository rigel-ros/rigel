from rigel.files.decoder import HEADER_SHARED_DATA, YAMLDataDecoder
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
        shared_data: Dict[str, Any] = {}  # noqa
    ) -> None:

        self.global_data = global_data
        self.application = application
        self.providers_data = providers_data
        self.shared_data = shared_data

        decoder = YAMLDataDecoder()
        self.raw_data = decoder.decode(
            raw_data,
            shared_data,
            HEADER_SHARED_DATA
        )

    def setup(self) -> None:
        """Use this function to allocate plugin resoures.
        """
        pass

    def start(self) -> None:
        """Use this function to start executing business logic of your plugin.
        """
        pass

    def process(self) -> None:
        """Use this function to perform any evaluation of your plugin execution.
        """
        pass

    def stop(self) -> None:
        """Use this function to gracefully clean plugin resources.
        """
        pass
