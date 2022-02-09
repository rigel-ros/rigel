from .image import ImageConfigurationFile
from dataclasses import asdict
from jinja2 import Template
from pkg_resources import resource_string
from rigel.loggers import MessageLogger


class Renderer:
    """
    A class that creates Dockerfiles.
    """
    @staticmethod
    def render(configuration_file: ImageConfigurationFile, template: str, output: str) -> None:
        """
        Create a new Dockerfile.
        Dockerfiles are always placed inside the .rigel_config directory.

        :type configuration_file: rigel.files.ImageConfigurationFile
        :param configuration_file: A data aggregator holding information about the containerization of the ROS application.
        :type template: string
        :param template: Name of the template file to render.
        :type output: string
        :param output: Name for the output rendered file.
        """
        # Open file template.
        dockerfile_template = resource_string(__name__, f'assets/templates/{template}').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        with open(f'.rigel_config/{output}', 'w+') as output_file:
            output_file.write(dockerfile_templater.render(configuration=asdict(configuration_file)))
            MessageLogger.info(f"Created {output}.")
