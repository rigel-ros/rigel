import docker
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
        :param image: The name of the Docker image to build.
        :type build_args: dict
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

        # Log state messages during the build process.
        iterator = iter(temp)
        while True:
            try:
                log = next(iterator)
                if 'stream' in log:
                    print(log['stream'].strip('\n'))
            except StopIteration:  # no more log messages
                if 'error' in log:
                    print(f'An error occurred while building Docker image {image}.')
                else:
                    print(f'Docker image {image} was built with success.')
                break
