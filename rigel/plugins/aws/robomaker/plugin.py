import boto3
import time
from rigel.clients import ROSBridgeClient
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers.aws import AWSProviderOutputModel
from rigel.plugins.plugin import Plugin as PluginBase
from rigel.plugins.core.test.introspection.command import CommandHandler
from rigel.plugins.core.test.introspection.parser import SimulationRequirementsParser
from rigel.plugins.core.test.introspection.requirements.manager import SimulationRequirementsManager
from typing import Any, Dict, List
from .models import PluginModel

LOGGER = get_logger()

ROBOT_APPLICATION = 'rigel_robomaker_robot_application'
SIMULATION_APPLICATION = 'rigel_robomaker_simulation_application'


class Plugin(PluginBase):

    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any]
    ) -> None:
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data
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

    def create_robot_application(
        self,
        application_name: str
    ) -> Dict[str, Any]:
        kwargs = {
            'name': application_name,
            'robotSoftwareSuite': {
                'name': 'General'
            },
            'environment': {
                'uri': self.model.robot_application.ecr
            }
        }
        robot_application = self.__robomaker_client.create_robot_application(**kwargs)
        LOGGER.info("Robot application created with success")
        return robot_application

    def delete_robot_application(
        self,
        arn: str
    ) -> None:
        kwargs = {'application': arn}
        self.__robomaker_client.delete_robot_application(**kwargs)
        LOGGER.info("Robot application deleted with success")

    def create_simulation_application(
        self,
        application_name: str
    ) -> Dict[str, Any]:
        kwargs = {
            'name': application_name,
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
        LOGGER.info("Simulation application created with success")
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
        if self.model.data_sources:
            kwargs['dataSources'] = [source.dict() for source in self.model.data_sources]

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

    def setup(self) -> None:
        self.__robomaker_client = self.retrieve_robomaker_client()
        self.__robot_application = self.create_robot_application(ROBOT_APPLICATION)
        self.__simulation_application = self.create_simulation_application(SIMULATION_APPLICATION)
        self.__simulation_job = self.create_simulation_job()

    def run(self) -> None:
        self.wait_simulation_job_status('Running')
        simulation_job_public_ip = self.__simulation_job['networkInterface']['publicIpAddress']
        print(f'Simulation job can be accessed on {simulation_job_public_ip}')

        self.__requirements_manager = SimulationRequirementsManager(self.model.simulation_duration * 1.0)
        self.__requirements_parser = SimulationRequirementsParser()

        requirements = self.model.robot_application.requirements
        if requirements:

            nodes: List[CommandHandler] = [
                self.__requirements_parser.parse(req) for req in requirements
            ]

            self.__requirements_manager.children = nodes

            # Connect to ROS bridge inside container
            port = self.model.robot_application.ports[0][0]
            rosbridge_client = ROSBridgeClient(simulation_job_public_ip, port)
            LOGGER.info(f"Connected to ROS bridge server at '{simulation_job_public_ip}:{port}'")

            self.__requirements_manager.connect_to_rosbridge(rosbridge_client)

        LOGGER.info("Testing the application!")

        while self.__requirements_manager.children and (not self.__requirements_manager.assess_children_nodes()):
            pass  # TODO: separate this into a thread for efficiency
        print(self.__requirements_manager)

    def stop(self) -> None:
        self.cancel_simulation_job(self.__simulation_job['arn'])
        self.delete_robot_application(self.__robot_application['arn'])
        self.delete_simulation_application(self.__simulation_application['arn'])
