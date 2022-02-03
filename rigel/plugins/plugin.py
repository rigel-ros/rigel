import docker
from typing import Protocol


class RegistryPlugin(Protocol):
    """
    This class specifies the interface that all plugins used to deploy containerized ROS
    applications must comply with.
    """

    def tag(client: docker.api.client.APIClient, image: str) -> None:
        """
        Use this function to set the image tag for the Docker image of the ROS application, if required.

        :type client: docker.api.client.APIClient
        :type client: A Docker client instance.
        :type image: str
        :type image: The current name for the Docker image.
        """
        ...

    def authenticate(client: docker.api.client.APIClient) -> None:
        """
        Use this function to authenticate with the image registry.

        :type client: docker.api.client.APIClient
        :type client: A Docker client instance.
        """
        ...

    def deploy(client: docker.api.client.APIClient) -> None:
        """
        Use this function to push the Docker image of the ROS application to the desired image registry.

        :type client: docker.api.client.APIClient
        :type client: A Docker client instance.
        """
        ...


class SimulationPlugin(Protocol):
    """
    This class specifies the interface that all plugins used to run containerized ROS
    applications must comply with.
    """

    def simulate(*args, **kwargs) -> None:
        """
        Use this function to launch the containerized ROS application.
        """
        ...
