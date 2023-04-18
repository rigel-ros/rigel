import signal
from rigel.exceptions import RigelError
from rigel.executor import (
    ConcurrentStagesExecutor,
    ParallelStageExecutor,
    SequentialStageExecutor,
    StageExecutor
)
from rigel.files.decoder import YAMLDataDecoder
from rigel.files.loader import YAMLDataLoader
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginDataModel
from rigel.models.rigelfile import Rigelfile
from rigel.models.sequence import (
    ConcurrentStage,
    ParallelStage,
    Sequence,
    SequenceJobEntry,
    SequentialStage
)
from rigel.providers.manager import ProviderManager
from rigel.providers.provider import Provider
from typing import Any, Dict, List, Optional, Union

LOGGER = get_logger()


class Orchestrator:

    def __init__(self, rigelfile: str) -> None:
        """Class constructor.
        Job orchestrator.

        :rigelfile: path to Rigelfile.
        :type: str
        """

        # Parse YAML Rigelfile
        loader = YAMLDataLoader(rigelfile)
        decoder = YAMLDataDecoder()
        yaml_data = decoder.decode(loader.load())

        # Initialize internal data structures
        self.rigelfile: Rigelfile = ModelBuilder(Rigelfile).build([], yaml_data)
        assert isinstance(self.rigelfile, Rigelfile)

        self.providers: List[Provider] = []
        self.providers_data: Dict[str, Any] = {}
        self.__provider_manager: ProviderManager = ProviderManager()
        self.__job_shared_data: Dict[str, Any] = {}

        self.__current_stage: Optional[StageExecutor] = None

        # Initialize providers
        self.initializate_providers()

    def initializate_providers(self) -> None:
        for provider_id, provider_data in self.rigelfile.providers.items():
            self.providers.append(
                self.__provider_manager.load(
                    provider_data.provider,
                    provider_id,
                    provider_data.with_,
                    self.rigelfile.vars,
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
        print()  # to avoid ^C character on the same line
        LOGGER.error('Stopping execution')
        if self.__current_stage:
            self.__current_stage.cancel()
            self.__current_stage = None
        # print(self.__job_shared_data)
        exit(1)

    def get_job_data(
        self,
        job: Union[str, SequenceJobEntry]
    ) -> PluginDataModel:

        try:

            if isinstance(job, str):
                job_identifier = job
                job_data = self.rigelfile.jobs[job_identifier]

            else:  # isinstance(job, SequenceJobEntry)
                job_identifier = job.name
                job_data = self.rigelfile.jobs[job_identifier]
                job_data.with_.update(job.with_)

            return job_data

        except KeyError:
            raise RigelError(f"Unknown job '{job_identifier}'")

    def create_sequential_executor(self, stage: SequentialStage) -> SequentialStageExecutor:
        return SequentialStageExecutor(
            [self.get_job_data(job) for job in stage.jobs]
        )

    def create_concurrent_executor(self, stage: ConcurrentStage) -> ConcurrentStagesExecutor:
        return ConcurrentStagesExecutor(
            [self.get_job_data(job) for job in stage.jobs],
            [self.get_job_data(job) for job in stage.dependencies],
        )

    def create_parallel_executor(self, stage: ParallelStage) -> ParallelStageExecutor:
        inner_stages = []
        for inner_stage in stage.parallel:
            if isinstance(inner_stage, SequentialStage):
                inner_stages.append(self.create_sequential_executor(inner_stage))
            elif isinstance(inner_stage, ConcurrentStage):
                inner_stages.append(self.create_concurrent_executor(inner_stage))

        return ParallelStageExecutor(inner_stages, stage.matrix)

    def generate_execution_plan(self, sequence: Sequence) -> List[StageExecutor]:
        """Generate an execution plan from a sequence of jobs.

        :param sequence: the sequence of jobs
        :type sequence: Sequence
        :return: an execution plan
        :rtype: List[StageExecutor]
        """
        execution_plan: List[StageExecutor] = []
        for stage in sequence.stages:

            if isinstance(stage, ParallelStage):
                executor = self.create_parallel_executor(stage)
            elif isinstance(stage, SequentialStage):
                executor = self.create_sequential_executor(stage)
            elif isinstance(stage, ConcurrentStage):
                executor = self.create_concurrent_executor(stage)

            execution_plan.append(executor)

        return execution_plan

    def execute(self, execution_plan: List[StageExecutor]) -> None:
        """Run an execution plan.

        :param execution_plan: the execution plan to be executed
        :type execution_plan: List[StageExecutor]
        """
        for stage in execution_plan:
            self.__current_stage = stage
            stage.job_shared_data = self.__job_shared_data
            stage.execute(
                self.rigelfile.vars,
                self.rigelfile.application,
                self.providers_data
            )
        # print(self.__job_shared_data)
        self.__current_stage = None

    def run_job(self, job: str) -> None:
        """Run a single job.

        :param job: The job identifier.
        :type job: str
        """
        # Create a wrapper sequence for the single job being executed
        sequence = Sequence(
            stages=[SequentialStage(jobs=[job])]
        )

        execution_plan = self.generate_execution_plan(sequence)

        self.handle_signals()
        self.connect_providers()
        self.execute(execution_plan)
        self.disconnect_providers()

    def run_sequence(self, name: str) -> None:
        """Run a sequence of jobs.

        :param sequence: The sequence identifier.
        :type sequence: str
        """
        sequence = self.rigelfile.sequences.get(name, None)
        if not sequence:
            raise RigelError(f"Sequence '{name}' not found")

        execution_plan = self.generate_execution_plan(sequence)

        self.handle_signals()
        self.connect_providers()
        self.execute(execution_plan)
        self.disconnect_providers()
