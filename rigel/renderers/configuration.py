from jinja2 import Template
from pkg_resources import resource_string


class RigelConfigurationRenderer:

    # TODO: use copy instead of Jinja for this operation
    @staticmethod
    def render() -> None:

        # Open template of Dockerfile.
        rigelfile_template = resource_string(__name__, 'templates/Rigelfile.j2').decode('utf-8')
        rigelfile_templater = Template(rigelfile_template)

        # Render Dockerfile for each robot
        with open('Rigelfile', 'w+') as output_file:
            output_file.write(rigelfile_templater.render())
