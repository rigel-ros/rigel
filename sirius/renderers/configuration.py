from jinja2 import Template
from pkg_resources import resource_string


class SiriusConfigurationRenderer:

    # TODO: use copy instead of Jinja for this operation
    @staticmethod
    def render() -> None:

        # Open template of Dockerfile.
        sirius_template = resource_string(__name__, 'templates/Sirius.j2').decode('utf-8')
        sirius_templater = Template(sirius_template)

        # Render Dockerfile for each robot
        with open('Sirius', 'w+') as output_file:
            output_file.write(sirius_templater.render())
