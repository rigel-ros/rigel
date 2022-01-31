import docker
from typing import Protocol


class RegistryPlugin(Protocol):
    """
    A contract that all external plugins must adhere to.
    """

    def tag(client: docker.api.client.APIClient, image: str) -> None:
        ...

    def authenticate(client: docker.api.client.APIClient) -> None:
        ...

    def deploy(client: docker.api.client.APIClient) -> None:
        ...


class SimulationPlugin(Protocol):

    def simulate(client: docker.api.client.APIClient, *args, **kwargs) -> None:
        ...
