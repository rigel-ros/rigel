from argparse import ArgumentParser
from pathlib import Path
from sirius.parsers import ConfigurationFileParser
from sirius.renderers import DockerfileRenderer, EntrypointRenderer, SiriusConfigurationRenderer, SSHConfigurationFileRenderer
from sys import exit


def main() -> None:

    # Create main parser
    cli_parser = ArgumentParser(description='Sirius - containerize and deploy your ROS application using Docker.')
    cli_parser.add_argument('command', type=str, help='the command to execute')
    cli_args = cli_parser.parse_args()

    if cli_args.command == 'init':

        SiriusConfigurationRenderer.render()

    elif cli_args.command == 'render':

        Path(".sirius_config").mkdir(parents=True, exist_ok=True)
        configuration_parser = ConfigurationFileParser('./Sirius')

        DockerfileRenderer.render(configuration_parser.configuration_file)
        EntrypointRenderer.render(configuration_parser.configuration_file)
        if configuration_parser.configuration_file.ssh:
            SSHConfigurationFileRenderer.render(configuration_parser.configuration_file)

    else:
        print(f'Invalid command "{cli_args.command}"')
        exit(1)


if __name__ == '__main__':
    main()
