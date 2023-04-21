import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from python_on_whales.components.container.cli_wrapper import Container
from python_on_whales.exceptions import DockerException
from rigel.clients import DockerClient
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict, List, Optional, Tuple
from .models import PluginModel, ApplicationComponent

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

    def create_simulation_network(self) -> None:
        """
        Create dedicated Docker network created for a simulation.
        """
        self.__docker_client.create_network(self.__network_name, 'bridge')
        LOGGER.info(f"Created Docker network '{self.__network_name}'")

    def start_dns_server(self) -> None:
        dns_container = f'rigel-dns-{self.__simulation_uuid}'
        self.__docker_client.run_container(
            dns_container,
            'dvdarias/docker-hoster',
            detach=True,
            networks=[self.__network_name],
            privileged=True,
            volumes=[
                ('/var/run/docker.sock', '/tmp/docker.sock'),
                ('/etc/hosts', '/tmp/hosts')
            ]
        )
        LOGGER.info(f"Created DNS server '{dns_container}'")

    def stop_dns_server(self) -> None:
        dns_container = f'rigel-dns-{self.__simulation_uuid}'
        self.__docker_client.remove_container(dns_container)
        LOGGER.info(f"Stopped DNS server '{dns_container}'")

    def start_ros_master(self) -> None:
        master_container = f'master-{self.__simulation_uuid}'
        self.__docker_client.run_container(
            master_container,
            f'ros:{self.application.distro}',
            hostname=master_container,
            command=['roscore'],
            envs={
                'ROS_HOSTNAME': master_container,
                'ROS_MASTER_URI': f'http://{master_container}:11311'
            },
            networks=[self.__network_name],
            detach=True
        )
        LOGGER.info(f"Created ROS master '{master_container}'")

    def stop_ros_master(self) -> None:
        master_container = f'master-{self.__simulation_uuid}'
        self.__docker_client.remove_container(master_container)
        LOGGER.info(f"Stopped ROS master '{master_container}'")

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
        master_container = f'master-{self.__simulation_uuid}'
        self.__docker_client.wait_for_container_status(master_container, 'running')
        master_container = self.__docker_client.get_container(master_container)
        assert master_container
        master_ip = master_container.network_settings.networks[self.__network_name].ip_address

        # Start containerize ROS application
        for test_component in self.model.components:

            container = self.run_package_container(test_component, master_ip)
            # container = self.run_package_container(test_component, master_container)

            if container:

                container_ip = container.network_settings.networks[self.__network_name].ip_address
                LOGGER.info(f"Created container '{test_component.name}-{self.__simulation_uuid}' ({container_ip} -> {master_ip})")

    def run_package_container(self, component: ApplicationComponent, master: str) -> Optional[Container]:
        """
        Launch a single containerized ROS node.

        :type component: ApplicationComponent
        :param component: Information about the test component.
        :type master: str
        :param master: The IP address of the ROS MASTER.

        :rtype: docker.models.containers.Container
        :return: The Docker container serving as ROS master.
        """
        component_name = f"{component.name}-{self.__simulation_uuid}"
        kwargs = component._kwargs.copy()

        kwargs['detach'] = True
        kwargs['hostname'] = component_name

        if 'envs' not in kwargs:
            kwargs['envs'] = {}
        kwargs['envs']['ROS_MASTER_URI'] = f'http://{master}:11311'
        kwargs['envs']['ROS_HOSTNAME'] = f"{kwargs['hostname']}"

        # TODO: ensure that networks can be costumized.
        # Probably not required.
        kwargs['networks'] = [self.__network_name]

        if 'restart' not in kwargs:
            kwargs['restart'] = 'on-failure'

        self.__docker_client.run_container(
            component_name,
            component.image,
            **kwargs
        )
        self.__docker_client.wait_for_container_status(component_name, 'running')

        if component.introspection:
            self.shared_data["simulation_address"] = component_name

        return self.__docker_client.get_container(component_name)  # this call to 'get_container' ensures updated container data

    def remove_package_containers(self) -> None:
        """Remove a single containerized ROS node.

        :type plugin: PluginModel
        :param plugin: Test components for this package.
        """
        for test_component in self.model.components:
            component_name = f"{test_component.name}-{self.__simulation_uuid}"
            self.__docker_client.remove_container(component_name)
            LOGGER.info(f"Removed Docker container '{component_name}'")

    def copy_files(self) -> None:
        """Copy files from a container to the host system.
        """
        root_path = f"/home/{os.environ.get('USER')}/.rigel/archives/test"
        base_path = Path(f"{root_path}/{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}")
        latest_path = Path(f"{root_path}/latest")

        copied_files = False
        for test_component in self.model.components:

            component_name = f"{test_component.name}-{self.__simulation_uuid}"

            component_container = self.__docker_client.get_container(component_name)
            assert isinstance(component_container, Container)

            if test_component.artifacts:

                base_path.mkdir(parents=True, exist_ok=True)

                LOGGER.info(f"Saving files from component '{component_name}':")
                for file in test_component.artifacts:

                    complete_file_path = Path(f"{base_path}/{component_name}")
                    complete_file_path.mkdir(parents=True, exist_ok=True)

                    try:

                        component_container.copy_from(Path(file), complete_file_path)

                        filename = file.rsplit('/')[-1]
                        LOGGER.info(f"- {file} -> {str(complete_file_path.absolute())}/{filename}")
                        copied_files = True

                    except DockerException:

                        LOGGER.warning(f"File '{file}' does not exist inside container. Ignoring.")

        if copied_files:

            if latest_path.exists():
                latest_path.unlink()
            latest_path.symlink_to(base_path)

    def setup(self) -> None:
        self.create_simulation_network()
        self.start_dns_server()
        self.start_ros_master()

    def start(self) -> None:
        """
        Plugin entrypoint.
        Create simulation network and all containers required for a given simulation.
        """
        self.bringup_ros_nodes()

    def process(self) -> None:

        LOGGER.info("Press CTRL-C/CTRL-Z to stop plugin execution.")

        if self.model.timeout:
            time.sleep(self.model.timeout)
        else:
            LOGGER.warning("Containers will run indefinitely since no timeout value was provided.")
            while True:
                pass  # do nothing until user CTRL-Z

    def stop(self) -> None:
        """
        Plugin graceful closing mechanism.
        """
        self.copy_files()
        self.stop_ros_master()
        self.stop_dns_server()
        self.remove_package_containers()
        self.remove_simulation_network()
