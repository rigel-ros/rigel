from argparse import ArgumentParser
from base64 import b64decode
from boto3 import client as aws_client
from botocore.exceptions import ClientError
from docker import APIClient, from_env
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
        registry_name = configuration_parser.configuration_file.registry.name
        image_name = configuration_parser.configuration_file.image.name
        image_tag = configuration_parser.configuration_file.image.tag
        complete_image_name = f'{registry_name}/{image_name}:{image_tag}'
        print(f"Building Docker image {complete_image_name}.")

        buildargs = {}
        for key in configuration_parser.configuration_file.ssh:
            if not key.file:
                buildargs[key.value] = environ.get(key.value)

        # Extracted and adapted from:
        # https://stackoverflow.com/questions/43540254/how-to-stream-the-logs-in-docker-python-api
        docker_client = APIClient(base_url='tcp://docker:2375')
        # docker_client = APIClient(base_url='unix:///var/run/docker.sock')
        image = docker_client.build(
            path='.',
            dockerfile='.sirius_config/Dockerfile',
            tag=complete_image_name,
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
                print(f'Docker image {complete_image_name} build complete.')
                break
            except ValueError:
                print(f'Unable to parse log from Docker image being build ({complete_image_name}): {log}')

    elif cli_args.command == 'deploy':

        configuration_parser = ConfigurationFileParser('./Sirius')
        registry_name = configuration_parser.configuration_file.registry.name
        image_name = configuration_parser.configuration_file.image.name
        image_tag = configuration_parser.configuration_file.image.tag
        complete_image_name = f'{registry_name}/{image_name}:{image_tag}'

        try:

            # Extracted and adapted from:
            # https://github.com/AlexIoannides/py-docker-aws-example-project/blob/master/deploy_to_aws.py
            print(f'Authenticate with a registry.AWS ECR ({configuration_parser.configuration_file.registry.name})')

            aws_ecr = aws_client(
                'ecr',
                aws_access_key_id=environ.get('AWS_ACCESS_KEY'),
                aws_secret_access_key=environ.get('AWS_SECRET_KEY'),
                region_name=environ.get('AWS_REGION')
            )
            aws_token = b64decode(aws_ecr.get_authorization_token()['authorizationData'][0]['authorizationToken']).replace(b'AWS:', b'').decode('utf-8')

            docker_client = from_env()
            docker_client.login(
                username=configuration_parser.configuration_file.registry.user,
                password=aws_token,
                registry=configuration_parser.configuration_file.registry.name
            )

        except ClientError:
            print('Invalid AWS credentials.')
            exit(1)

        print(f'Pushing image {complete_image_name} to ECR.')
        image = docker_client.images.push(
            complete_image_name,
            stream=True,
            decode=True,
            auth_config={
                'username': configuration_parser.configuration_file.registry.user,
                'password': aws_token
            }
        )
        image_logs = iter(image)
        while True:
            try:
                log = next(image_logs)
                if 'progess' in log:
                    print(log['progress'].strip('\n'))
            except StopIteration:
                print(f'Image {complete_image_name} was pushed with success to ECR.')
                break
            except ValueError:
                print(f'Unable to parse log from Docker image being build ({complete_image_name}): {log}')

    else:
        print(f'Invalid command "{cli_args.command}"')
        exit(1)


if __name__ == '__main__':
    main()
