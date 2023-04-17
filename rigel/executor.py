import copy
import threading
from rigel.models.sequence import (
    ConcurrentStage,
    SequentialStage
)
from rigel.loggers import get_logger
from rigel.plugins.plugin import Plugin
from typing import Any, Dict, List, Optional, Union

LOGGER = get_logger()


class StageExecutor:

    job_shared_data: Dict[str, Any] = {}

    def cancel(self) -> None:
        raise NotImplementedError

    def execute(self) -> None:
        raise NotImplementedError


class ExecutionBranch(threading.Thread):

    def __init__(
        self,
        stage: Union[SequentialStage, ConcurrentStage],
        job_shared_data: Dict[str, Any]
    ) -> None:
        super(ExecutionBranch, self).__init__()

        self.executor = stage
        assert isinstance(self.executor, StageExecutor)

        self.executor.job_shared_data = job_shared_data

    def cancel(self) -> None:
        self.executor.cancel()

    def run(self) -> None:
        self.executor.execute()


class ParallelStageExecutor(StageExecutor):

    def __init__(self, stages: List[Union[SequentialStage, ConcurrentStage]]) -> None:
        self.stages = stages
        self.threads = []

    def cancel(self) -> None:
        for thread in self.threads:
            thread.cancel()

    def execute(self) -> None:

        # TODO: consider / implement a mechanism that allows shared plugin data to passed
        # from a ParallelStageExecutor instance to other stage executors

        for stage in self.stages:

            # NOTE: a deep copy of data is passed to each thread
            # to avoid conflicts

            self.threads.append(
                ExecutionBranch(stage, copy.deepcopy(self.job_shared_data))
            )

        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()


class SequentialStageExecutor(StageExecutor):

    def __init__(self, jobs: List[Plugin]) -> None:
        self.jobs = jobs
        self.current_job: Optional[Plugin] = None

    def cancel(self) -> None:
        if self.current_job:
            self.current_job.stop()
            self.current_job = None

    def execute(self) -> None:
        for job in self.jobs:

            assert isinstance(job, Plugin)
            self.current_job = job

            job.shared_data = self.job_shared_data
            job.setup()
            job.start()
            job.process()
            job.stop()

        self.current_job = None


class ConcurrentStagesExecutor(StageExecutor):

    def __init__(self, jobs: List[Plugin], dependencies: List[Plugin]) -> None:
        self.jobs = jobs
        self.dependencies = dependencies
        self.current_job: Optional[Plugin] = None

    def cancel(self) -> None:

        if self.current_job:
            self.current_job.stop()
            self.current_job = None

        for job in self.dependencies:
            job.stop()

    def execute(self) -> None:

        for job in self.dependencies:
            assert isinstance(job, Plugin)
            job.shared_data = self.job_shared_data
            job.setup()
            job.start()

        for job in self.jobs:
            assert isinstance(job, Plugin)
            self.current_job = job
            job.shared_data = self.job_shared_data
            job.setup()
            job.start()
            job.process()
            job.stop()

        self.current_job = None

        for job in self.dependencies:
            job.stop()
