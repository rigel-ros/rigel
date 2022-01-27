from argparse import ArgumentParser
from docker import APIClient, from_env
from io import BytesIO
from json import loads as json_loads
from os import environ
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

    elif cli_args.command == 'build':

        configuration_parser = ConfigurationFileParser('./Sirius')
        image_tag = configuration_parser.configuration_file.image
        print(f"Building Docker image {image_tag}.")

        buildargs = {}
        for key in configuration_parser.configuration_file.ssh:
            if not key.file:
                buildargs[key.value] = environ.get(key.value)

        # Extracted and adapted from:
        # https://stackoverflow.com/questions/43540254/how-to-stream-the-logs-in-docker-python-api
        docker_client = APIClient(base_url='tcp://docker:2375')
        image = docker_client.build(
            path='.',
            dockerfile='.sirius_config/Dockerfile',
            tag=image_tag,
            buildargs=buildargs,
            rm=True,
        )
        image_logs = iter(image)
        while True:
            try:
                log = next(image_logs)
                log = log.strip(b'\r\n')
                json_log = json_loads(log)
                if 'stream' in json_log:
                    print(json_log['stream'].strip('\n'))
            except StopIteration:
                print(f'Docker image {image_tag} build complete.')
                break
            except ValueError:
                print(f'Unable to parse log from Docker image being build ({image_tag}): {log}')

    else:
        print(f'Invalid command "{cli_args.command}"')
        exit(1)


if __name__ == '__main__':
    main()
