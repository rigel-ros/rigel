import boto3
import time
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers.aws import AWSProviderOutputModel
from rigel.plugins.plugin import Plugin as PluginBase
from typing import Any, Dict, List, Optional
from .models import PluginModel, DataSource

LOGGER = get_logger()


class Plugin(PluginBase):

    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any] = {}  # noqa
    ) -> None:
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)
        assert isinstance(self.model, PluginModel)

    def retrieve_robomaker_client(self) -> boto3.session.Session.client:

        providers = [provider for _, provider in self.providers_data.items() if isinstance(provider, AWSProviderOutputModel)]

        if not providers:
            raise RigelError(base='No AWS provider were found. This plugin requires a connection to AWS RoboMaker.')
        elif len(providers) > 1:
            raise RigelError(base='Multiple AWS providers was found. Please specify which provider you want to use.')
        else:
            client = providers[0].robomaker_client
            if not client:
                raise RigelError(base='Selected AWS provider is not configured to work with AWS RoboMaker.')
            return client

    def create_robot_application(self) -> Dict[str, Any]:
        kwargs = {
            'name': self.model.robot_application.name,
            'robotSoftwareSuite': {
                'name': 'General'
            },
            'environment': {
                'uri': self.model.robot_application.ecr
            }
        }
        robot_application = self.__robomaker_client.create_robot_application(**kwargs)
        LOGGER.info(f"New robot application '{self.model.robot_application.name}' created with success")
        return robot_application

    def delete_robot_application(
        self,
        arn: str
    ) -> None:
        kwargs = {'application': arn}
        self.__robomaker_client.delete_robot_application(**kwargs)
        LOGGER.info("Robot application deleted with success")

    def create_simulation_application(self) -> Dict[str, Any]:
        kwargs = {
            'name': self.model.simulation_application.name,
            'robotSoftwareSuite': {
                'name': 'General'
            },
            'simulationSoftwareSuite': {
                'name': 'SimulationRuntime'
            },
            'environment': {
                'uri': self.model.simulation_application.ecr
            }
        }
        simulation_application = self.__robomaker_client.create_simulation_application(**kwargs)
        LOGGER.info(f"New simulation application '{self.model.simulation_application.name}' created with success")
        return simulation_application

    def delete_simulation_application(
        self,
        arn: str
    ) -> None:
        kwargs = {'application': arn}
        self.__robomaker_client.delete_simulation_application(**kwargs)
        LOGGER.info("Simulation application deleted with success")

    def convert_envs(self, envs: List[str]) -> Dict[str, str]:
        result = {}
        for env in envs:
            key, value = env.split('=')
            result[key.strip()] = value.strip()
        return result

    def create_simulation_job(self) -> Dict[str, Any]:
        kwargs = {
            'iamRole': self.model.iam_role,
            'outputLocation': {'s3Bucket': self.model.output_location} if self.model.output_location else {},
            'maxJobDurationInSeconds': self.model.simulation_duration,
            'robotApplications': [
                {
                    'application': self.__robot_application['arn'],
                    'launchConfig': {
                        'streamUI': self.model.robot_application.streamUI,
                        'command': self.model.robot_application.command,
                        'environmentVariables': self.convert_envs(self.model.robot_application.environment),
                        'portForwardingConfig': {
                            'portMappings': [
                                {
                                    'jobPort': ports[0],
                                    'applicationPort': ports[1],
                                    'enableOnPublicIp': True
                                }
                                for ports in self.model.robot_application.ports
                            ]
                        },
                    },
                    'tools': [tool.dict() for tool in self.model.robot_application.tools]
                }
            ],
            'simulationApplications': [
                {
                    'application': self.__simulation_application['arn'],
                    'launchConfig': {
                        'streamUI': self.model.simulation_application.streamUI,
                        'command': self.model.simulation_application.command,
                        'environmentVariables': self.convert_envs(self.model.simulation_application.environment),
                        'portForwardingConfig': {
                            'portMappings': [
                                {
                                    'jobPort': ports[0],
                                    'applicationPort': ports[1],
                                    'enableOnPublicIp': True
                                }
                                for ports in self.model.simulation_application.ports
                            ]
                        },
                    },
                    'worldConfigs': [config.dict() for config in self.model.simulation_application.worldConfigs],
                    'tools': [tool.dict() for tool in self.model.simulation_application.tools]
                }
            ],
            'vpcConfig': {
                'subnets': self.model.vpc_config.subnets,
                'securityGroups': self.model.vpc_config.securityGroups,
                'assignPublicIp': self.model.vpc_config.assignPublicIp
            },
        }

        # Prepare data sources and WorldForge exports
        kwargs['dataSources'] = [source.dict() for source in self.model.data_sources]

        # Check if a custom WorldForge export job was provided in the Rigelfile.
        worldforge_exported_jobs = [
            source for source in self.model.data_sources if source.s3Keys[0].startswith('aws-robomaker-worldforge-export')
        ]

        if not worldforge_exported_jobs:

            # Ensure that at least a WorldForge export job was provided
            if not self.model.worldforge_exported_job:
                raise RigelError("No WorldForge world was provided as a data source")

            kwargs['dataSources'].append(
                DataSource(
                    name='ExportedWorldJob',
                    type='Archive',
                    **self.shared_data['worldforge_exported_job']
                ).dict()
            )

        simulation_job = self.__robomaker_client.create_simulation_job(**kwargs)
        LOGGER.info('Created simulation job')
        return simulation_job

    def cancel_simulation_job(self, arn: str) -> None:
        kwargs = {'job': arn}
        self.__robomaker_client.cancel_simulation_job(**kwargs)
        LOGGER.info('Simulation job canceled with success')

    def wait_simulation_job_status(self, status: str) -> None:
        kwargs = {'job': self.__simulation_job['arn']}
        LOGGER.info(f"Waiting for simulation job status to be '{status}'")
        while True:
            simulation_job_data = self.__robomaker_client.describe_simulation_job(**kwargs)
            if simulation_job_data['status'] == status:
                self.__simulation_job = simulation_job_data
                break
            time.sleep(0.5)

    def get_robot_application(self) -> Optional[Dict[str, Any]]:
        kwargs = {
            "maxResults": 1,
            "filters":
            [
                {
                    "name": "name",
                    "values": [self.model.robot_application.name]
                }
            ]
        }
        response = self.__robomaker_client.list_robot_applications(**kwargs)
        if response['robotApplicationSummaries']:
            LOGGER.info(f"Found existing robot application '{self.model.robot_application.name}'")
            return response['robotApplicationSummaries'][0]
        return None

    def get_simulation_application(self) -> Optional[Dict[str, Any]]:
        kwargs = {
            "maxResults": 1,
            "filters":
            [
                {
                    "name": "name",
                    "values": [self.model.simulation_application.name]
                }
            ]
        }
        response = self.__robomaker_client.list_simulation_applications(**kwargs)
        if response['simulationApplicationSummaries']:
            LOGGER.info(f"Found existing simulation application '{self.model.simulation_application.name}'")
            return response['simulationApplicationSummaries'][0]
        return None

    def setup(self) -> None:
        self.__robomaker_client = self.retrieve_robomaker_client()
        self.__robot_application = self.get_robot_application() or self.create_robot_application()
        self.__simulation_application = self.get_simulation_application() or self.create_simulation_application()
        self.__simulation_job = self.create_simulation_job()

    def start(self) -> None:

        self.wait_simulation_job_status('Running')

        simulation_job_public_ip = self.__simulation_job['networkInterface']['publicIpAddress']
        simulation_job_public_port = self.model.robot_application.ports[0][0]
        simulation_job_duration = self.model.simulation_duration

        print(f'Simulation job can be accessed on {simulation_job_public_ip}:{simulation_job_public_port}')

        self.shared_data["simulation_address"] = simulation_job_public_ip
        self.shared_data["simulation_port"] = simulation_job_public_port
        self.shared_data["simulation_duration"] = simulation_job_duration

    def stop(self) -> None:
        self.cancel_simulation_job(self.__simulation_job['arn'])
        self.delete_robot_application(self.__robot_application['arn'])
        self.delete_simulation_application(self.__simulation_application['arn'])
