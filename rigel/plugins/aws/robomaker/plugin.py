import boto3
import time
from botocore.exceptions import ClientError as BotocoreClientError
from rigel.clients import ROSBridgeClient
from rigel.exceptions import ClientError
from rigel.loggers import get_logger
from rigel.models.package import Target
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

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)
        self.prepare_targets()

    def prepare_targets(self) -> None:
        self.__targets = [
            (package_name, package, PluginModel(**plugin_data))
            for package_name, package, plugin_data in self.targets]

    def authenticate(self, plugin: PluginModel) -> boto3.session.Session.client:
        """
        Authenticate with AWS RoboMaker.
        """
        try:

            # Obtain Robomaker authentication token
            robomaker_client = boto3.client(
                'robomaker',
                aws_access_key_id=plugin.credentials.aws_access_key_id,
                aws_secret_access_key=plugin.credentials.aws_secret_access_key,
                region_name=plugin.credentials.region_name
            )

        except BotocoreClientError as err:
            raise ClientError('AWS', err)

        LOGGER.info('Authenticated with AWS RoboMaker.')
        return robomaker_client

    def create_robot_application(
        self,
        application_name: str,
        plugin: PluginModel
    ) -> Dict[str, Any]:
        kwargs = {
            'name': application_name,
            'robotSoftwareSuite': {
                'name': 'General'
            },
            'environment': {
                'uri': plugin.robot_application.ecr
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
        application_name: str,
        plugin: PluginModel
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
                'uri': plugin.simulation_application.ecr
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

    def create_simulation_job(self, plugin: PluginModel) -> Dict[str, Any]:
        kwargs = {
            'iamRole': plugin.iam_role,
            'outputLocation': {'s3Bucket': plugin.output_location} if plugin.output_location else {},
            'maxJobDurationInSeconds': plugin.simulation_duration,
            'robotApplications': [
                {
                    'application': self.__robot_application['arn'],
                    'launchConfig': {
                        'command': plugin.robot_application.command,
                        'environmentVariables': self.convert_envs(plugin.robot_application.environment),
                        'portForwardingConfig': {
                            'portMappings': [
                                {
                                    'jobPort': ports[0],
                                    'applicationPort': ports[1],
                                    'enableOnPublicIp': True
                                }
                                for ports in plugin.robot_application.ports
                            ]
                        },
                    },
                    'tools': [tool.dict() for tool in plugin.robot_application.tools]
                }
            ],
            'simulationApplications': [
                {
                    'application': self.__simulation_application['arn'],
                    'launchConfig': {
                        'command': plugin.simulation_application.command,
                        'environmentVariables': self.convert_envs(plugin.simulation_application.environment),
                        'portForwardingConfig': {
                            'portMappings': [
                                {
                                    'jobPort': ports[0],
                                    'applicationPort': ports[1],
                                    'enableOnPublicIp': True
                                }
                                for ports in plugin.simulation_application.ports
                            ]
                        },
                    },
                    'tools': [tool.dict() for tool in plugin.simulation_application.tools]
                }
            ],
            'dataSources': [source.dict() for source in plugin.data_sources],
            'vpcConfig': {
                'subnets': plugin.vpc_config.subnets,
                'securityGroups': plugin.vpc_config.securityGroups,
                'assignPublicIp': plugin.vpc_config.assignPublicIp
            },
        }
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
        assert len(self.__targets) == 1, "RoboMakerPlugin does not support multiple targets!"
        for _, _, plugin_model in self.__targets:
            self.__robomaker_client = self.authenticate(plugin_model)

            self.__robot_application = self.create_robot_application(ROBOT_APPLICATION, plugin_model)
            self.__simulation_application = self.create_simulation_application(SIMULATION_APPLICATION, plugin_model)
            self.__simulation_job = self.create_simulation_job(plugin_model)

    def run(self) -> None:
        """
        Plugin entry point.
        """
        assert len(self.__targets) == 1, "RoboMakerPlugin does not support multiple targets!"
        for _, _, plugin_model in self.__targets:

            self.wait_simulation_job_status('Running')
            simulation_job_public_ip = self.__simulation_job['networkInterface']['publicIpAddress']
            print(f'Simulation job can be accessed on {simulation_job_public_ip}')

            self.__requirements_manager = SimulationRequirementsManager(plugin_model.simulation_duration * 1.0)
            self.__requirements_parser = SimulationRequirementsParser()

            requirements = plugin_model.robot_application.requirements
            if requirements:

                nodes: List[CommandHandler] = [
                    self.__requirements_parser.parse(req) for req in requirements
                ]

                self.__requirements_manager.children = nodes

                # Connect to ROS bridge inside container
                port = plugin_model.robot_application.ports[0][0]
                rosbridge_client = ROSBridgeClient(simulation_job_public_ip, port)
                LOGGER.info(f"Connected to ROS bridge server at '{simulation_job_public_ip}:{port}'")

                self.__requirements_manager.connect_to_rosbridge(rosbridge_client)

            LOGGER.info("Testing the application!")

            while self.__requirements_manager.children and (not self.__requirements_manager.assess_children_nodes()):
                pass  # TODO: separate this into a thread for efficiency
            print(self.__requirements_manager)

    def stop(self) -> None:
        assert len(self.__targets) == 1, "RoboMakerPlugin does not support multiple targets!"
        self.cancel_simulation_job(self.__simulation_job['arn'])
        self.delete_robot_application(self.__robot_application['arn'])
        self.delete_simulation_application(self.__simulation_application['arn'])
