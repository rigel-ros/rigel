from dataclasses import asdict
from jinja2 import Template
from pkg_resources import resource_string
from rigel.files import ImageConfigurationFile


class DockerfileRenderer:

    @staticmethod
    def render(configuration_file: ImageConfigurationFile) -> None:

        # Open template of Dockerfile.
        dockerfile_template = resource_string(__name__, 'templates/Dockerfile.j2').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        # Render Dockerfile for each robot
        with open('.rigel_config/Dockerfile', 'w+') as output_file:
            output_file.write(dockerfile_templater.render(dockerfile=asdict(configuration_file)))
