from .image import ImageConfigurationFile
from dataclasses import asdict
from jinja2 import Template
from pkg_resources import resource_string
from rigel.loggers import MessageLogger


class DockerfileRenderer:
    """
    A class that creates Dockerfiles.
    """

    @staticmethod
    def render(configuration_file: ImageConfigurationFile) -> None:
        """
        Create a new Dockerfile.
        Dockerfiles are always placed inside the .rigel_config directory.

        :type configuration_file: rigel.files.ImageConfigurationFile
        :param configuration_file: A data aggregator holding information about the containerization of the ROS application.
        """
        # Open file template.
        dockerfile_template = resource_string(__name__, 'assets/templates/Dockerfile.j2').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        with open('.rigel_config/Dockerfile', 'w+') as output_file:
            output_file.write(dockerfile_templater.render(dockerfile=asdict(configuration_file)))
            MessageLogger.info("Created Dockerfile")


class EntrypointRenderer:
    """
    A class that creates the 'entrypoint.sh' script.
    This script contains all setup commands that are to be executed at runtime.
    """

    @staticmethod
    def render(configuration_file: ImageConfigurationFile) -> None:
        """
        Creates an 'entrypoint.sh' script.
        The said script is always placed inside the .rigel_config directory.

        :type configuration_file: rigel.files.ImageConfigurationFile
        :param configuration_file: A data aggregator holding information about the containerization of the ROS application.
        """

        # Open file template.
        entrypoint_template = resource_string(__name__, 'assets/templates/entrypoint.j2').decode('utf-8')
        entrypoint_templater = Template(entrypoint_template)

        with open('.rigel_config/entrypoint.sh', 'w+') as output_file:
            output_file.write(entrypoint_templater.render(entrypoint=asdict(configuration_file)))
            MessageLogger.info("Created entrypoint.sh")


class SSHConfigurationFileRenderer:
    """
    A class that creates a SSH config file.
    This file consists of a mapping between private SSH keys and their associated hosts and is
    required to download private code repositories while containerizing a ROS application.
    """

    @staticmethod
    def render(configuration_file: ImageConfigurationFile) -> None:
        """
        Creates a SSH config file.
        The said file is always placed inside the .rigel_config directory.

        :type configuration_file: rigel.files.ImageConfigurationFile
        :param configuration_file: A data aggregator holding information about the containerization of the ROS application.
        """

        # Open file template.
        ssh_config_template = resource_string(__name__, 'assets/templates/config.j2').decode('utf-8')
        ssh_config_templater = Template(ssh_config_template)

        with open('.rigel_config/config', 'w+') as output_file:
            output_file.write(ssh_config_templater.render(config=asdict(configuration_file)))
            MessageLogger.info("Created SSH configuration file")
