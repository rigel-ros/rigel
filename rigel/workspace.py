import signal
from rigel.files.decoder import YAMLDataDecoder
from rigel.files.loader import YAMLDataLoader
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginDataModel
from rigel.models.rigelfile import Rigelfile
from rigel.plugins.manager import PluginManager
from rigel.plugins.plugin import Plugin
from rigel.providers.manager import ProviderManager
from rigel.providers.provider import Provider
from typing import Any, Dict, List, Optional

LOGGER = get_logger()


class WorkspaceManager:

    def __init__(self, path: str) -> None:
        """Class constructor.
        Retrieve workspace information from a Rigelfile.

        :path: path to Rigelfile.
        :type: str
        """
        # Parse YAML Rigelfile
        loader = YAMLDataLoader(path)
        decoder = YAMLDataDecoder()
        yaml_data = decoder.decode(loader.load())

        # Initialize internal data structures
        self.workspace: Rigelfile = ModelBuilder(Rigelfile).build([], yaml_data)
        assert isinstance(self.workspace, Rigelfile)

        self.providers: List[Provider] = []
        self.providers_data: Dict[str, Any] = {}
        self.__active_plugin: Optional[Plugin] = None
        self.__plugin_manager: PluginManager = PluginManager()
        self.__provider_manager: ProviderManager = ProviderManager()

        # Initialize providers
        self.initializate_providers()

    def initializate_providers(self) -> None:
        for provider_id, provider_data in self.workspace.providers.items():
            self.providers.append(
                self.__provider_manager.load(
                    provider_data.provider,
                    provider_id,
                    provider_data.with_,
                    self.workspace.vars,
                    self.providers_data
                )
            )

    def connect_providers(self) -> None:
        """Initialize and connect to all declared providers.
        """
        LOGGER.info("Connecting to providers")
        for provider in self.providers:
            provider.connect()

    def disconnect_providers(self) -> None:
        """Disconnect from all declared providers.
        """
        LOGGER.info("Disconnecting from providers")
        for provider in self.providers:
            provider.disconnect()

    def handle_signals(self) -> None:
        """Start listening for abort (CTRL-C and CTRL-Z) events.
        """
        signal.signal(signal.SIGINT, self.handle_abort)
        signal.signal(signal.SIGTSTP, self.handle_abort)
        LOGGER.warning("Press CTRL-C / CTRL-Z to stop execution")

    def handle_abort(self, *args: Any) -> None:
        """Handle abort events.
        Ensure that executing plugin is properly terminated and disconnect
        from all declared providers.
        """
        print('Stopping execution...')
        if self.__active_plugin:
            self.__active_plugin.stop()
            self.__active_plugin = None
        self.disconnect_providers()
        exit(1)

    def execute_plugin(self, job: str) -> None:
        """Run the plugin associated with a given job.

        :param job: The job identifier.
        :type job: str
        """
        for application_id, application_data in self.workspace.applications.items():

            LOGGER.info(f"Working with application '{application_id}'")

            if job in application_data.jobs:

                job_data = application_data.jobs[job]
                assert isinstance(job_data, PluginDataModel)

                self.__active_plugin = self.__plugin_manager.load(
                    job_data.plugin,
                    job_data.with_,
                    self.workspace.vars,
                    application_data,
                    self.providers_data
                )
                self.__active_plugin.setup()
                self.__active_plugin.run()
                self.__active_plugin.stop()
                self.__active_plugin = None

    def run_job(self, job: str) -> None:
        """Run a single job.

        :param job: The job identifier.
        :type job: str
        """
        self.handle_signals()
        self.connect_providers()
        self.execute_plugin(job)
        self.disconnect_providers()

    def run_sequence(self, sequence: str) -> None:
        """Run a sequence of jobs.

        :param sequence: The sequence identifier.
        :type sequence: str
        """
        self.handle_signals()
        self.connect_providers()
        if sequence in self.workspace.sequences:
            for job in self.workspace.sequences[sequence]:
                self.execute_plugin(job)
        self.disconnect_providers()
