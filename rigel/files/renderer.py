from jinja2 import Template
from pkg_resources import resource_string
from rigel.models import DockerSection


class Renderer:
    """
    A class that creates Dockerfiles.
    """

    def __init__(self, configuration_file: DockerSection) -> None:
        """
        :type configuration_file: rigel.models.DockerSection
        :param configuration_file: An aggregator of information about the containerization of the ROS application.
        """
        self.configuration_file = configuration_file

    def render(self, template: str, output: str) -> None:
        """
        Create a new Dockerfile.
        Dockerfiles are always placed inside the .rigel_config directory.

        :type template: string
        :param template: Name of the template file to render.
        :type output: string
        :param output: Name for the output rendered file.
        """
        # Open file template.
        dockerfile_template = resource_string(__name__, f'assets/templates/{template}').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        with open(output, 'w+') as output_file:
            output_file.write(dockerfile_templater.render(configuration=self.configuration_file.dict()))
