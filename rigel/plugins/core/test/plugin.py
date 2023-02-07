import uuid
from python_on_whales.components.container.cli_wrapper import Container
from rigel.clients import DockerClient, ROSBridgeClient
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict, List, Optional, Tuple
from .models import PluginModel, TestComponent
from .introspection.command import CommandHandler
from .introspection.requirements.manager import SimulationRequirementsManager
from .introspection.parser import SimulationRequirementsParser

LOGGER = get_logger()


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

        self.__simulation_uuid = str(uuid.uuid1())
        self.__network_name = f'rigel-simulation-{self.__simulation_uuid}'
        self.__docker_client = DockerClient()
        self.__requirements_manager = SimulationRequirementsManager(10 * 60.0)
        self.__requirements_parser = SimulationRequirementsParser()

    def create_simulation_network(self) -> None:
        """
        Create dedicated Docker network created for a simulation.
        """
        self.__docker_client.create_network(self.__network_name, 'bridge')
        LOGGER.info(f"Created Docker network '{self.__network_name}'")

    def start_dns_server(self) -> None:
        self.__docker_client.run_container(
            'rigel-dns',
            'dvdarias/docker-hoster',
            detach=True,
            networks=[self.__network_name],
            privileged=True,
            volumes=[
                ('/var/run/docker.sock', '/tmp/docker.sock'),
                ('/etc/hosts', '/tmp/hosts')
            ]
        )
        LOGGER.info("Created DNS server")

    def stop_dns_server(self) -> None:
        self.__docker_client.remove_container('rigel-dns')
        LOGGER.info("Stopped DNS server")

    def start_ros_master(self) -> None:
        self.__docker_client.run_container(
            'master',
            f'ros:{self.application.distro}',
            hostname='master',
            command=['roscore'],
            envs={
                'ROS_HOSTNAME': 'master',
                'ROS_MASTER_URI': 'http://master:11311'
            },
            networks=[self.__network_name],
            detach=True
        )
        LOGGER.info("Created ROS master")

    def stop_ros_master(self) -> None:
        self.__docker_client.remove_container('master')
        LOGGER.info("Stopped ROS master")

    def remove_simulation_network(self) -> None:
        """
        Remove dedicated Docker network created for a simulation.
        """
        self.__docker_client.remove_network(self.__network_name)
        LOGGER.info(f"Removed Docker network '{self.__network_name}'")

    def convert_envs(self, envs: List[str]) -> Dict[str, str]:
        result = {}
        for env in envs:
            key, value = env.split('=')
            result[key.strip()] = value.strip()
        return result

    def convert_volumes(self, volumes: List[str]) -> List[Tuple[str, ...]]:
        result = []
        for volume in volumes:
            result.append(tuple(volume.split(':')))
        return result

    def bringup_ros_nodes(self) -> None:
        """
        Launch all containerized ROS nodes required for a given simulation.
        """
        self.__docker_client.wait_for_container_status('master', 'running')
        master_container = self.__docker_client.get_container('master')
        assert master_container
        master_ip = master_container.network_settings.networks[self.__network_name].ip_address

        # Start containerize ROS application
        for test_component in self.model.components:

            container = self.run_package_container(test_component, master_ip)

            if container:

                container_ip = container.network_settings.networks[self.__network_name].ip_address
                LOGGER.info(f"Created container '{test_component.name}' ({container_ip})")

                if test_component.introspection:

                    requirements: List[CommandHandler] = [
                        self.__requirements_parser.parse(req) for req in test_component.introspection.requirements
                    ]

                    self.__requirements_manager.add_children(requirements)

                    # Connect to ROS bridge inside container
                    hostname = test_component.introspection.hostname or container_ip
                    port = test_component.introspection.publish[0]
                    rosbridge_client = ROSBridgeClient(hostname, port)
                    LOGGER.info(f"Connected to ROS bridge server at '{hostname}:{port}'")

                    self.__requirements_manager.connect_to_rosbridge(rosbridge_client)

    def run_package_container(self, component: TestComponent, master: str) -> Optional[Container]:
        """
        Launch a single containerized ROS node.

        :type component: TestComponent
        :param component: Information about the test component.
        :type master: str
        :param master: The IP address of the ROS MASTER.

        :rtype: docker.models.containers.Container
        :return: The Docker container serving as ROS master.
        """
        kwargs = component._kwargs.copy()

        kwargs['detach'] = True
        kwargs['hostname'] = component.name

        if 'envs' not in kwargs:
            kwargs['envs'] = {}
        kwargs['envs']['ROS_MASTER_URI'] = f'http://{master}:11311'
        kwargs['envs']['ROS_HOSTNAME'] = f"{kwargs['hostname']}"

        # TODO: ensure that networks can be costumized.
        # Probably not required.
        kwargs['networks'] = [self.__network_name]

        if 'restart' not in kwargs:
            kwargs['restart'] = 'on-failure'

        if component.introspection:
            if 'publish' not in kwargs:
                kwargs['publish'] = [component.introspection.publish]
            else:
                kwargs['publish'] = kwargs['publish'] + [component.introspection.publish]

        self.__docker_client.run_container(
            component.name,
            component.image,
            **kwargs
        )
        self.__docker_client.wait_for_container_status(component.name, 'running')
        return self.__docker_client.get_container(component.name)  # this call to 'get_container' ensures updated container data

    def remove_package_containers(self) -> None:
        """Remove a single containerized ROS node.

        :type plugin: PluginModel
        :param plugin: Test components for this package.
        """
        for test_component in self.model.components:
            self.__docker_client.remove_container(test_component.name)
            LOGGER.info(f"Removed Docker container '{test_component.name}'")

    def setup(self) -> None:
        self.create_simulation_network()
        self.start_dns_server()
        self.start_ros_master()

    def run(self) -> None:
        """
        Plugin entrypoint.
        Create simulation network and all containers required for a given simulation.
        """
        self.bringup_ros_nodes()
        LOGGER.info("Testing the application!")

        while not self.__requirements_manager.finished:
            pass  # TODO: separate this into a thread for efficiency
        print(self.__requirements_manager)

    def stop(self) -> None:
        """
        Plugin graceful closing mechanism.
        """
        self.stop_ros_master()
        self.stop_dns_server()
        self.remove_package_containers()
        self.remove_simulation_network()
