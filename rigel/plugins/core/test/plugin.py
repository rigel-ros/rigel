from rigel.clients import ROSBridgeClient
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict, List
from .models import PluginModel
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

        self.__requirements_manager = SimulationRequirementsManager(self.model.timeout)
        self.__requirements_parser = SimulationRequirementsParser()

    def connect_to_rosbridge_server(self) -> None:
        """
        Launch all containerized ROS nodes required for a given simulation.
        """
        requirements: List[CommandHandler] = [
            self.__requirements_parser.parse(req) for req in self.model.requirements
        ]

        self.__requirements_manager.add_children(requirements)

        # Connect to ROS bridge inside container
        hostname = self.shared_data.get("simulation_address", None) or self.model.hostname
        port = self.shared_data.get("simulation_port", None) or self.model.port

        rosbridge_client = ROSBridgeClient(hostname, port)
        LOGGER.info(f"Connected to ROS bridge server at '{hostname}:{port}'")

        self.__requirements_manager.connect_to_rosbridge(rosbridge_client)

    def start(self) -> None:
        """
        Plugin entrypoint.
        Connect to the ROS system to be tested.
        """
        self.connect_to_rosbridge_server()
        LOGGER.info("Testing the application!")

        while not self.__requirements_manager.finished:
            pass

        print(self.__requirements_manager)
