import uuid
from python_on_whales.components.container.cli_wrapper import Container
from rigel.clients import DockerClient
# from rigel.clients import DockerClient, ROSBridgeClient
from rigel.loggers import get_logger
from rigel.models.package import Target
from rigel.plugins import Plugin as PluginBase
from typing import List, Optional
from .models import PluginModel
from .introspection.requirements.manager import SimulationRequirementsManager
# from .introspection.parser import SimulationRequirementsParser

LOGGER = get_logger()


class Plugin(PluginBase):

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)

        self.__simulation_uuid = str(uuid.uuid1())
        self.__network_name = f'rigel-simulation-{self.__simulation_uuid}'
        self.__docker_client = DockerClient()
        self.__requirements_manager = SimulationRequirementsManager(5 * 60.0)
        # self.__requirements_parser = SimulationRequirementsParser()

    def create_simulation_network(self) -> None:
        """
        Create dedicated Docker network created for a simulation.
        """
        self.__docker_client.create_network(self.__network_name, 'bridge')
        LOGGER.info(f"Created Docker network '{self.__network_name}'")

    def remove_simulation_network(self) -> None:
        """
        Remove dedicated Docker network created for a simulation.
        """
        self.__docker_client.remove_network(self.__network_name)
        LOGGER.info(f"Removed Docker network '{self.__network_name}'")

    def bringup_ros_nodes(self) -> None:
        """
        Launch all containerized ROS nodes required for a given simulation.
        """
        # Start containerize ROS application
        for package, plugin in self.__targets:

            ros_common_env_variables = ['ROS_MASTER_URI=http://master:11311', f'ROS_HOSTNAME={package}']

            # Ensure that all ROS nodes connect to the same ROS master node
            assert plugin.environment is not None  # NOTE: required by mypy to ensure that the addition is possible
            plugin.environment = plugin.environment + ros_common_env_variables

            container = self.run_package_container(package, plugin)

            if container:

                container_ip = container.network_settings.ip_address
                LOGGER.info(f"Created container '{package}' ({container_ip})")

                # if plugin.introspection:

                #     requirements = [self.__requirements_parser.parse(requirement) for requirement in plugin.introspection]
                #     self.__requirements_manager.children = requirements

                #     # Connect to ROS bridge inside container
                #     rosbridge_client = ROSBridgeClient(container_ip, 9090)
                #     LOGGER.info(f"Connected to ROS bridge server at '{container_ip}:9090'")

                #     self.__requirements_manager.connect_to_rosbridge(rosbridge_client)

    def run_package_container(self, package: str, plugin: PluginModel) -> Optional[Container]:
        """
        Launch a single containerized ROS node.

        :type package: str
        :param package: Identifier of the containerized package.
        :type plugin: PluginModel
        :param plugin: Information about the container.

        :rtype: docker.models.containers.Container
        :return: The Docker container serving as ROS master.
        """
        self.__docker_client.run_container(
            package,
            plugin.image,
            command=plugin.command,
            detach=True,
            environment=plugin.environment,
            hostname=package,
            network=self.__network_name,
            privileged=plugin.privileged,
            volumes=plugin.volumes
        )
        self.__docker_client.wait_for_container_status(package, 'running')
        return self.__docker_client.get_container(package)  # this call to 'get_container' ensures updated container data

    def remove_package_container(self, package: str) -> None:
        """Remove a single containerized ROS node.

        :type package: str
        :param package: Identifier of the containerized package.
        """
        self.__docker_client.remove_container(package)
        LOGGER.info(f"Removed Docker container '{package}'")

    def setup(self) -> None:
        self.__targets = [
            (package, PluginModel(**plugin_data))
            for package, _, plugin_data in self.targets]

        # Inject container with ROS master node
        self.__targets.insert(
            0,
            ('master', PluginModel(image=f'ros:{self.distro}', command='roscore'))
        )

        self.create_simulation_network()

    def run(self) -> None:
        """
        Plugin entrypoint.
        Create simulation network and all containers required for a given simulation.
        """
        self.bringup_ros_nodes()
        while not self.__requirements_manager.children or not self.__requirements_manager.finished:
            pass
        LOGGER.info(self.__requirements_manager)

    def stop(self) -> None:
        """
        Plugin graceful closing mechanism.
        """
        # Remove containers
        for package, _ in self.__targets:
            self.remove_package_container(package)

        self.remove_simulation_network()