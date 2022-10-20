import python_on_whales
import time
from rigel.exceptions import (
    DockerAPIError,
    InvalidDockerClientInstanceError
)
from rigel.loggers import get_logger
from typing import Any, Iterable, Optional, Tuple, Union


MESSAGE_LOGGER = get_logger()


class DockerClient:
    """
    A wrapper class for the docker.client.DockerClient.
    Keeps the same functionality but allows for error handling that suits better Rigel.
    """

    DOCKER_CONTAINER_ID_DISPLAY_SIZE: int = 12
    DOCKER_RUN_TIMEOUT: int = 120  # seconds
    DOCKER_RUN_WAIT_STATUS: int = 3  # seconds

    # A Docker client instance.
    client: python_on_whales.docker_client.DockerClient

    def __init__(self, client: Optional[python_on_whales.docker_client.DockerClient] = None) -> None:
        """
        Create a Docker client instance.

        :type client: Optional[python_on_whales.docker_client.DockerClient]
        :param client: A Docker client instance.
        """
        if client:
            if isinstance(client, InvalidDockerClientInstanceError):
                self.client = client
            else:
                raise InvalidDockerClientInstanceError()
        else:
            self.client = python_on_whales.docker

    def __getattribute__(self, __name: str) -> Any:

        # Wrapper for 'python_on_whales.docker_client.DockerClient'.
        # Look for arguments inside wrapped class before throwing an AttributeError.

        try:
            return object.__getattribute__(self, __name)
        except AttributeError:
            pass

        try:
            return object.__getattribute__(self.client, __name)
        except AttributeError:
            pass

        raise AttributeError(f"No 'DockerClient' object has attribute '{__name}'")

    def get_image(self, name: str) -> Optional[python_on_whales.components.image.cli_wrapper.Image]:
        """
        Get an existing Docker image.

        :type name: string
        :param name: The Docker image name.
        :rtype: Optional[python_on_whales.components.image.cli_wrapper.Image]
        :return: The Docker image if existent. None otherwise.
        """
        try:
            if self.client.image.exists(name):
                return self.client.image.inspect(name)
            else:
                return None
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def build_image(
        self,
        path: str,
        **kwargs: Any
    ) -> None:
        """
        Build a new Docker image.

        :type path: string
        :param path: Root of the build context.
        :type kwargs: Dict[str, Any]
        :param kwargs: Keyword arguments. Consult the documentation for more information
        (https://github.com/gabrieldemarmiesse/python-on-whales/blob/master/python_on_whales/components/buildx/cli_wrapper.py#L204)
        """
        try:
            self.client.build(
                path,
                **kwargs
            )
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def tag_image(self, source_image: str, target_image: str) -> None:
        """
        Create a Docker image that references an existing Docker image.

        :type source_image: string
        :param source_image: The name of the image being referenced.
        :type target_image: string
        :param target_image: The desired name for the new image.
        """
        try:
            self.client.image.tag(source_image, target_image)
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def push_image(self, image: str) -> None:
        """
        Push a Docker image to a Docker image registry.

        :type image: string
        :param image: The name of the Docker image.
        """
        try:
            self.client.image.push(image)
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def get_builder(self, name: str) -> Optional[python_on_whales.components.buildx.cli_wrapper.Builder]:
        """
        Get a Docker builder

        :param name: the name of the builder
        :type name: str
        :return: the builder, if existent
        :rtype: python_on_whales.components.buildx.cli_wrapper.Builder
        """
        try:
            return self.client.buildx.inspect(name)
        except python_on_whales.exceptions.DockerException:
            return None

    def create_builder(
        self,
        name: str,
        use: bool = True,
        driver: str = 'docker-container'
    ) -> python_on_whales.components.buildx.cli_wrapper.Builder:
        """
        Create a Docker builder.

        :param name: the builder name
        :type name: str
        :param use: set to use, defaults to True
        :type use: bool, optional
        :return: the created Docker builder, if unexistent.
        :rtype: python_on_whales.components.buildx.cli_wrapper.Builder
        """
        builder = self.get_builder(name)
        if not builder:
            try:
                return self.client.buildx.create(name=name, use=use, driver=driver)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception=exception)
        return builder  # return already existing builder

    def remove_builder(self, name: str) -> None:
        """
        Remove a Docker builder.

        :type name: string
        :param name: The name of the Docker builder.
        """
        builder = self.get_builder(name)
        if builder:
            try:
                self.client.buildx.remove(builder)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception=exception)

    def get_network(self, name: str) -> Optional[python_on_whales.components.network.cli_wrapper.Network]:
        """
        Get a Docker network.

        :type name: string
        :param name: The name of the Docker network.

        :rtype: Optional[python_on_whales.components.network.cli_wrapper.Network]
        :return: The Docker network with the specified name.
        """
        try:
            return self.client.network.inspect(name)
        except python_on_whales.exceptions.DockerException:
            return None

    def create_network(self, name: str, driver: str) -> python_on_whales.components.network.cli_wrapper.Network:
        """
        Create a Docker network.

        :type name: string
        :param name: The name of the Docker network.
        :type driver: string
        :param driver: Name of driver used to create the network.

        :rtype: python_on_whales.components.network.cli_wrapper.Network
        :return: The Docker network with the specified name.
        """
        network = self.get_network(name)
        if not network:
            try:
                return self.client.network.create(name, driver=driver)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception=exception)
        return network  # return already existing network

    def remove_network(self, name: str) -> None:
        """
        Remove a Docker network.

        :type name: string
        :param name: The name of the Docker network.
        """
        network = self.get_network(name)
        if network:
            try:
                self.client.network.remove(network)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception=exception)

    def get_container(self, name: str) -> Optional[python_on_whales.components.container.cli_wrapper.Container]:
        """
        Get a Docker container.

        :type name: string
        :param name: The name of the Docker container.

        :rtype: Optional[python_on_whales.components.container.cli_wrapper.Container]
        :return: The Docker container with the specified name.
        """
        try:
            if self.client.container.exists(name):
                return self.client.container.inspect(name)
            else:
                return None
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def run_container(
        self,
        name: str,
        image: str,
        **kwargs: Any
    ) -> Union[python_on_whales.components.container.cli_wrapper.Container, str, Iterable[Tuple[str, bytes]]]:
        """
        Run a Docker container with a given name.

        :type name: string
        :param name: The Docker container name.
        :type image: string
        :param name: The Docker image.
        :type kwargs: Dict[str, Any]
        :param kwargs: Keyword arguments. Consult the documentation for more information
        (https://gabrieldemarmiesse.github.io/python-on-whales/sub-commands/container/)

        :rtype: Union[python_on_whales.components.container.cli_wrapper.Container, str, Iterable[Tuple[str, bytes]]]
        :return: The created Docker container
        """
        container = self.get_container(name)
        if not container:
            kwargs['name'] = name
            try:
                return self.client.container.run(image, **kwargs)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception=exception)
        return container  # return already existing container

    def remove_container(self, name: str) -> None:
        """
        Remove a Docker container.

        :type name: string
        :param name: The name of the Docker container.
        """
        container = self.get_container(name)
        if container:
            try:
                container.remove(force=True, volumes=True)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception=exception)

    def wait_for_container_status(
            self,
            name: str,
            status: str
            ) -> None:
        """
        Wait for a container status to change to a desired value.

        :type name: string
        :param name: The name of the container to watch.
        :type status: string
        :param status: The desires container status.
        """

        elapsed_time = 0  # seconds
        while True:
            container = self.get_container(name)
            if container:
                if elapsed_time < self.DOCKER_RUN_TIMEOUT:
                    if container.state.status == status:
                        return
                    time.sleep(self.DOCKER_RUN_WAIT_STATUS)
                    elapsed_time = elapsed_time + self.DOCKER_RUN_WAIT_STATUS
                    MESSAGE_LOGGER.info('Waiting for status of container {} to become "{}". Current status is "{}".'.format(
                        container.id[:self.DOCKER_CONTAINER_ID_DISPLAY_SIZE],
                        status,
                        container.state.status
                    ))
                else:
                    raise DockerAPIError(exception=Exception(
                        'Timeout while waiting for status of container {} to become "{}".'.format(
                            container.id[:self.DOCKER_CONTAINER_ID_DISPLAY_SIZE],
                            status
                        )
                    ))
            else:
                raise DockerAPIError(exception=Exception(
                    f'Unable to watch over status of container "{name}" since it does not exist.'
                ))
