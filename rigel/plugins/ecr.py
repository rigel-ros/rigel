import base64
import docker
import os
from boto3 import client as aws_client
from botocore.exceptions import ClientError
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Plugin:

    account: int
    credentials: Dict[str, str]
    image: str
    region: str
    user: str
    token: str = field(default_factory=lambda: '')

    def __post_init__(self) -> None:

        # Ensure no declared field was left undefined.
        for field_name, field_value in self.__dict__.items():
            if field_value is None:
                print(f"Field '{field_name}' was declared but left undefined.")
                exit(1)

        # Ensure required credentials were provided.
        for credential in ['access_key', 'secret_access_key']:
            if self.credentials.get(credential) is None:
                print(f"Missing credentials or invalid value.")
                exit(1)

        self.registry = f'{self.account}.dkr.ecr.{self.region}.amazonaws.com'

    def tag(self, docker_client: docker.api.client.APIClient, image: str) -> None:

        if ':' in self.image:
            new_image_name, new_image_tag = self.image.split(':')
        else:
            new_image_name = self.image
            new_image_tag = 'latest'

        docker_client.tag(
            image=image,
            repository=f'{self.registry}/{new_image_name}',
            tag=new_image_tag
        )

        print(f"Set tag for Docker image '{self.image}' .")

    def authenticate(self, docker_client: docker.api.client.APIClient) -> None:

        try:

            # Obtain ECR authentication token
            aws_ecr = aws_client(
                'ecr',
                aws_access_key_id=os.environ.get(self.credentials['access_key']),
                aws_secret_access_key=os.environ.get(self.credentials['secret_access_key']),
                region_name=self.region
            )

            # Decode ECR authentication token
            token = aws_ecr.get_authorization_token()['authorizationData'][0]['authorizationToken']
            self.__token = base64.b64decode(token).replace(b'AWS:', b'').decode('utf-8')

        except ClientError:
            print('Invalid AWS credentials.')
            exit(1)

        # Authenticate with AWS ECR.
        docker_client.login(
            username=self.user,
            password=self.__token,
            registry=self.registry
        )

        print(f'Authenticated with AWS ECR ({self.registry})')

    def deploy(self, docker_client: docker.api.client.APIClient) -> None:

        complete_image_name = f'{self.registry}/{self.image}'

        image = docker_client.push(
            complete_image_name,
            stream=True,
            decode=True,
            auth_config={
                'username': self.user,
                'password': self.__token
            }
        )

        iterator = iter(image)
        while True:
            try:
                log = next(iterator)
                if 'progess' in log:
                    print(log['progress'].strip('\n'))

            except StopIteration:  # pushing operation finished
                if 'error' in log:
                    print(f'An error occurred while pushing image {complete_image_name} to AWS ECR.')
                else:
                    print(f'Image {complete_image_name} was pushed with success to AWS ECR.')
                break

            except ValueError:
                print(f'Unable to parse log message while pushing Docker image ({complete_image_name}): {log}')
