import copy
import itertools
import threading
from rigel.files.decoder import HEADER_SHARED_DATA, YAMLDataDecoder
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.plugin import PluginDataModel
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.models.sequence import (
    ConcurrentStage,
    SequentialStage
)
from rigel.plugins.manager import PluginManager
from rigel.plugins.plugin import Plugin
from typing import Any, Dict, List, Optional, Union


LOGGER = get_logger()


class StageExecutor:

    job_shared_data: Dict[str, Any] = {}

    def cancel(self) -> None:
        raise NotImplementedError

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
    ) -> None:
        raise NotImplementedError


class LoaderStageExecutor(StageExecutor):

    __plugin_manager: PluginManager = PluginManager()

    def load_plugin(
        self,
        job: PluginDataModel,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any],
        overwrite_data: Dict[str, Any] = {}  # noqa
    ) -> Plugin:
        """Load the Rigel plugin associated with a given job.

        :param job: The job identifier.
        :type job: Union[str, SequenceJobEntry]
        """

        job_raw_data = job.with_

        if overwrite_data:
            job_raw_data.update(overwrite_data)

        return self.__plugin_manager.load(
            job.plugin,
            job_raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )


class ExecutionBranch(threading.Thread):

    def __init__(
        self,
        stages: List[Union[SequentialStage, ConcurrentStage]],
        job_shared_data: Dict[str, Any],
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any]
    ) -> None:
        super(ExecutionBranch, self).__init__()

        self.stages = stages
        self.job_shared_data = job_shared_data

        self.__current_stage: Optional[Union[SequentialStage, ConcurrentStage]] = None

        self.__global_data = global_data
        self.__application = application
        self.__providers_data = providers_data

    def cancel(self) -> None:
        if self.__current_stage:
            self.__current_stage.stop()
            self.__current_stage = None

    def run(self) -> None:

        for stage in self.stages:
            self.__current_stage = stage
            stage.job_shared_data = self.job_shared_data
            stage.execute(
                self.__global_data,
                self.__application,
                self.__providers_data
            )

        self.__current_stage = None


class ParallelStageExecutor(StageExecutor):

    def __init__(self, stages: List[Union[SequentialStage, ConcurrentStage]], matrix: Dict[str, List[Any]]) -> None:
        self.stages = stages
        self.matrix = matrix
        self.threads = []

    def __combine_matrix_data(self, matrix: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        keys = matrix.keys()
        values = matrix.values()

        # NOTE: it returns [{}] if no matrix data was provided.
        # This ensures that 'execute' can always be called.

        combinations = list(itertools.product(*values))
        return [dict(zip(keys, combo)) for combo in combinations]

    def __decode_matrix_data(self) -> Dict[str, List[Any]]:

        decoder = YAMLDataDecoder()
        return decoder.decode(
            self.matrix,
            self.job_shared_data,
            HEADER_SHARED_DATA
        )

    def cancel(self) -> None:
        for thread in self.threads:
            thread.cancel()

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any]
    ) -> None:

        decoded_matrix = self.__decode_matrix_data()
        combinations = self.__combine_matrix_data(decoded_matrix)

        for combination in combinations:

            # NOTE: a deep copy of data is passed to each thread
            # to avoid conflicts
            local_shared_data = copy.deepcopy(self.job_shared_data)
            local_shared_data.update(combination)

            local_stages = copy.deepcopy(self.stages)

            self.threads.append(
                ExecutionBranch(
                    local_stages,
                    local_shared_data,
                    global_data,
                    application,
                    providers_data
                )
            )

        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()

        # TODO: consider / implement a mechanism that allows shared plugin data to passed
        # from a ParallelStageExecutor instance to other stage executors


class SequentialStageExecutor(LoaderStageExecutor):

    def __init__(self, jobs: List[PluginDataModel]) -> None:
        self.job_models = jobs
        self.__current_job: Optional[Plugin] = None

    def cancel(self) -> None:
        if self.__current_job:
            self.__current_job.stop()
            self.__current_job = None

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
    ) -> None:

        for job_model in self.job_models:

            job = self.load_plugin(
                job_model,
                global_data,
                application,
                providers_data,
                self.job_shared_data
            )
            assert isinstance(job, Plugin)

            self.__current_job = job

            job.setup()
            job.start()
            job.process()
            job.stop()

        self.__current_job = None


class ConcurrentStagesExecutor(LoaderStageExecutor):

    def __init__(self, jobs: List[PluginDataModel], dependencies: List[PluginDataModel]) -> None:
        self.job_models = jobs
        self.dependency_models = dependencies

        self.__current_job: Optional[Plugin] = None
        self.__dependencies: List[Plugin] = []

    def cancel(self) -> None:

        if self.__current_job:
            self.__current_job.stop()
            self.__current_job = None

        for job in self.__dependencies:
            job.stop()

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
    ) -> None:

        for job_model in self.dependency_models:

            job = self.load_plugin(
                job_model,
                global_data,
                application,
                providers_data,
                self.job_shared_data
            )
            self.__dependencies.append(job)
            assert isinstance(job, Plugin)

            job.setup()
            job.start()

        for job_model in self.job_models:

            job = self.load_plugin(
                job_model,
                global_data,
                application,
                providers_data,
                self.job_shared_data
            )
            assert isinstance(job, Plugin)

            self.__current_job = job

            job.setup()
            job.start()
            job.process()
            job.stop()

        self.__current_job = None

        for job in self.__dependencies:
            job.stop()
