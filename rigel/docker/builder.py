import docker
import os
from rigel.exceptions import DockerBuildError
from rigel.loggers import DockerLogPrinter
from rigel.models import DockerSection


class ImageBuilder:
    """
    A class to build Docker images.
    """

    def __init__(self, docker_client: docker.api.client.APIClient) -> None:
        """
        :rtype: docker.api.client.APIClient
        :return: A Docker client instance.
        """
        self.docker_client = docker_client

    def build(self, configuration: DockerSection) -> None:
        """
        Build a Docker image.

        :type configuration: rigel.models.DockerSection
        :param docker_client: Information regarding how to containerize the ROS package.
        """

        build_args = {}
        for key in configuration.ssh:
            build_args[key.value] = os.environ.get(key.value)

        # Build Docker image.
        temp = self.docker_client.build(
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
                break
