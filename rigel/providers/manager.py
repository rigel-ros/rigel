from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError
)
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict, Type
from .provider import Provider

LOGGER = get_logger()


class ProviderManager:

    def is_provider_compliant(self, entrypoint: Type) -> bool:
        """Ensure that a given provider entrypoint class is an instance of
        rigel.providers.Provider.

        :type entrypoint: Type
        :param entrypoint: The provider entrypoint class.

        :rtype: bool
        :return: True if the provider entrypoint class is an instance of
        rigel.providers.Provider. False otherwise.
        """
        return issubclass(entrypoint, Provider)

    def load(
        self,
        entrypoint: str,
        identifier: str,
        provider_raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any]
    ) -> Provider:
        """Instantiate a provider.

        :type entrypoint: str
        :param entrypoint: The provider entrypoint class.
        :type identifier: str
        :param identifier: The provider identifier.
        :type provider_raw_data: ProviderRawData
        :param provider_raw_data: The unprocessed providerr configuration data.
        :type global_data: RigelfileGlobalData
        :param global_data: The global data.
        :type providers_data: Dict[str, Any]
        :param providers_data: Dynamic data bank for providers.

        :rtype: Provider
        :return: An instance of the specified provider.
        """
        provider_complete_name = entrypoint.strip()
        provider_name, provider_entrypoint = provider_complete_name.rsplit('.', 1)

        try:
            module = import_module(provider_name)
            cls: Type = getattr(module, provider_entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(provider_complete_name)

        if not self.is_provider_compliant(cls):
            raise PluginNotCompliantError(
                provider_complete_name,
                "entrypoint class must inherit functions 'connect' and 'disconnect' from class 'Provider'."
            )

        provider = ModelBuilder(cls).build([
            identifier,
            provider_raw_data,
            global_data,
            providers_data
        ], {})

        assert isinstance(provider, Provider)
        return provider
