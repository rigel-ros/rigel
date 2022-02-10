import docker
import os
from rigel.exceptions import DockerBuildError
from rigel.loggers import DockerLogPrinter, MessageLogger
from rigel.files import ImageConfigurationFile


class ImageBuilder:
    """
    A class to build Docker images.
    """

    @staticmethod
    def build(configuration: ImageConfigurationFile) -> None:
        """
        Build a Docker image.

        :type configuration: rigel.files.ImageConfigurationFile
        :param docker_client: Information regarding the Docker build process.
        """

        def create_docker_client() -> docker.api.client.APIClient:
            """
            Create a Docker client instance.

            :rtype: docker.api.client.APIClient
            :return: A Docker client instance.
            """
            return docker.from_env().api

        build_args = {}
        for key in configuration.ssh:
            build_args[key.value] = os.environ.get(key.value)

        # Build Docker image.
        docker_client = create_docker_client()
        temp = docker_client.build(
            path='.',
            dockerfile='.rigel_config/Dockerfile',
            tag=configuration.image,
            buildargs=build_args,
            decode=True,
            rm=True,
        )

        printer = DockerLogPrinter()

        # Log state messages during the build process.
        iterator = iter(temp)
        while True:

            try:

                log = next(iterator)
                printer.log(log)

            except StopIteration:  # no more log messages
                if 'error' in log:
                    raise DockerBuildError(msg=log['error'])
                else:
                    MessageLogger.info(f'Docker image {configuration.image} was built with success.')

                break
