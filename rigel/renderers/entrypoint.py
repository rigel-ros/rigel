from dataclasses import asdict
from jinja2 import Template
from pkg_resources import resource_string
from rigel.files import ImageConfigurationFile


class EntrypointRenderer:

    @staticmethod
    def render(configuration_file: ImageConfigurationFile) -> None:

        # Open template of Dockerfile.
        entrypoint_template = resource_string(__name__, 'templates/entrypoint.j2').decode('utf-8')
        entrypoint_templater = Template(entrypoint_template)

        # Render Dockerfile for each robot
        with open('.rigel_config/entrypoint.sh', 'w+') as output_file:
            output_file.write(entrypoint_templater.render(entrypoint=asdict(configuration_file)))
