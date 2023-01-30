from rigel.loggers import get_logger
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict

LOGGER = get_logger()


class Provider:
    """This class specifies the interface that all providers must comply with.
    """

    def __init__(
        self,
        identifier: str,
        raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any],
    ) -> None:
        self.identifier = identifier
        self.raw_data = raw_data
        self.global_data = global_data
        self.providers_data = providers_data

    def connect(self) -> None:
        """Use this function to connect to required provider services.
        """
        pass

    def disconnect(self) -> None:
        """Use this function to gracefully diconnect from provider services.
        """
        pass
