import os
from rigel.models.builder import ModelBuilder
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers import Provider
from typing import Any, Dict
from .models import SSHKeyGroup, SSHProviderModel, SSHProviderOutputModel


class SSHProvider(Provider):

    def __init__(
        self,
        identifier: str,
        raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any]
    ) -> None:
        super().__init__(
            identifier,
            raw_data,
            global_data,
            providers_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(SSHProviderModel).build([], self.raw_data)
        assert isinstance(self.model, SSHProviderModel)

    def verify_env(self, key: SSHKeyGroup) -> SSHKeyGroup:
        if os.environ.get(key.env, None):
            return key
        else:
            raise Exception(f"Invalid SSH key value. Environment variable '{key.env}' is not set.")

    def verify_file(self, key: SSHKeyGroup) -> SSHKeyGroup:
        if os.path.isfile(key.path):
            return key
        else:
            raise Exception(f"Invalid SSH key path '{key.path}'. Either it does not exist or it is not a file.")

    def connect(self) -> None:
        for key in self.model.keys:
            if key.env:
                self.verify_env(key)
            else:  # key.path is set:
                self.verify_file(key)

        # NOTE: using ModelBuilder is required for the instance to update its class type despite
        # having the same content as the input model.
        self.providers_data[self.identifier] = ModelBuilder(SSHProviderOutputModel).build([], self.model.dict())

    def disconnect(self) -> None:
        pass  # do nothing
