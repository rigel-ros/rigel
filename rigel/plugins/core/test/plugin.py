from rigel.clients import ROSBridgeClient
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict, List, Optional
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

        # Ensure a reference exists to the ROS bridge client
        # to ensure safe stop at any moment
        self.__rosbridge_client: Optional[ROSBridgeClient] = None

        # Ensure a reference exists to the requirement introspection manager
        # to ensure safe stop at any moment
        self.__requirements_manager: Optional[SimulationRequirementsManager] = None

        assert isinstance(self.model, PluginModel)

    def connect_to_rosbridge_server(self) -> None:

        self.__rosbridge_client = ROSBridgeClient(self.model.hostname, self.model.port)
        self.__rosbridge_client.connect()
        LOGGER.info(f"Connected to ROS bridge server at '{self.model.hostname}:{self.model.port}'")

    def disconnect_from_rosbridge_server(self) -> None:
        if self.__rosbridge_client:
            self.__rosbridge_client.close()
            LOGGER.info(f"Disconnected from ROS bridge server at '{self.model.hostname}:{self.model.port}'")
        self.__rosbridge_client = None

    def start_introspection(self) -> None:

        requirements: List[CommandHandler] = [
            self.__requirements_parser.parse(req) for req in self.model.requirements
        ]

        self.__requirements_manager.add_children(requirements)
        self.__requirements_manager.connect_to_rosbridge(self.__rosbridge_client)

    def stop_introspection(self) -> None:

        if self.__requirements_manager:
            self.__requirements_manager.disconnect_from_rosbridge()

    def setup(self) -> None:

        self.connect_to_rosbridge_server()

        self.__requirements_manager = SimulationRequirementsManager(
            self.model.timeout * 1.0,
            self.model.ignore * 1.0
        )
        self.__requirements_parser = SimulationRequirementsParser()

    def start(self) -> None:
        """
        Plugin entrypoint.
        Connect to the ROS system to be tested.
        """
        self.start_introspection()

    def process(self) -> None:
        LOGGER.info("Testing the application!")
        while not self.__requirements_manager.finished:
            pass
        print(self.__requirements_manager)

    def stop(self) -> None:
        self.stop_introspection()
        self.disconnect_from_rosbridge_server()
