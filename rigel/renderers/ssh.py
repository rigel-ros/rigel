from dataclasses import asdict
from jinja2 import Template
from pkg_resources import resource_string
from rigel.files import ImageConfigurationFile


class SSHConfigurationFileRenderer:

    @staticmethod
    def render(configuration_file: ImageConfigurationFile) -> None:

        # Open template of Dockerfile.
        ssh_config_template = resource_string(__name__, 'templates/config.j2').decode('utf-8')
        ssh_config_templater = Template(ssh_config_template)

        # Render Dockerfile for each robot
        with open(f'.rigel_config/config', 'w+') as output_file:
            output_file.write(ssh_config_templater.render(config=asdict(configuration_file)))
