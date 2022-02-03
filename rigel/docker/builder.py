import docker
from rigel.loggers import DockerLogPrinter, MessageLogger
from typing import Any, Dict


class ImageBuilder:
    """
    A class to build Docker images.
    """

    @staticmethod
    def build(docker_client: docker.api.client.APIClient, image: str, build_args: Dict[str, Any] = {}) -> None:
        """
        Build a Docker image.

        :type docker_client: docker.api.client.APIClient
        :param docker_client: A Docker client instance.
        :type image: string
        :param image: The final name for the Docker image.
        :type build_args: Dict[string, Any]
        :param build_args: A dictionary holding the values of all arguments declared in the Dockerfile.
        """

        # Build Docker image.
        temp = docker_client.build(
            path='.',
            dockerfile='.rigel_config/Dockerfile',
            tag=image,
            buildargs=build_args,
            decode=True,
            rm=True,
        )

        printer = DockerLogPrinter()

        # Log state messages during the build process.
        iterator = iter(temp)
        while True:

            try:

                # TODO: add printer for each type of message.
                log = next(iterator)
                printer.log(log)

            except StopIteration:  # no more log messages
                if 'error' in log:
                    MessageLogger.error(f'An error occurred while building Docker image {image}.')
                else:
                    MessageLogger.info(f'Docker image {image} was built with success.')

                break
