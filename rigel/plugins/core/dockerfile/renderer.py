from jinja2 import Template
from pkg_resources import resource_string
from pydantic import BaseModel


class Renderer:
    """A class that creates Dockerfiles.
    """

    def __init__(self, configuration_file: BaseModel) -> None:
        """
        :type configuration_file: pydantic.BaseModel
        :param configuration_file: An aggregator of information about the containerization of the ROS application.
        """
        self.configuration_file = configuration_file

    def render(self, template: str, output: str) -> None:
        """
        Create a new Dockerfile.

        :type template: string
        :param template: Name of the template file to render.
        :type output: string
        :param output: Name for the output rendered file.
        """

        # Open file template.
        dockerfile_template = resource_string(__name__, f'assets/{template}').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        with open(output, 'w+') as output_file:
            output_file.write(dockerfile_templater.render(configuration=self.configuration_file.dict()))
