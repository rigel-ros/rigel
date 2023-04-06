import threading
from rigel.models.sequence import (
    ConcurrentStage,
    ParallelStage,
    Sequence,
    SequentialStage
)
from rigel.loggers import get_logger
from rigel.plugins.plugin import Plugin
from typing import List, Optional, Union

LOGGER = get_logger()


class StageExecutor:

    def cancel(self) -> None:
        raise NotImplementedError

    def execute(self) -> None:
        raise NotImplementedError


class ExecutionBranch(threading.Thread):

    def __init__(self, stage: Union[SequentialStage, ConcurrentStage]) -> None:
        super(ExecutionBranch, self).__init__()
        self.executor = stage

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
        for stage in self.stages:
            self.threads.append(ExecutionBranch(stage))

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
            job.setup()
            job.start()

        for job in self.jobs:
            assert isinstance(job, Plugin)
            self.current_job = job
            job.setup()
            job.start()
            job.process()
            job.stop()

        self.current_job = None

        for job in self.dependencies:
            job.stop()


if __name__ == '__main__':

    sequence = Sequence(
        stages=[
            ParallelStage(
                description="Build the required Docker images",
                parallel=[
                    ["dockerfile_robot", "build_robot"],
                    ["dockerfile_simulation", "build_simulation"]
                ]
            ),
            ConcurrentStage(
                description="Ensure application works as expected",
                core=["introspection_job"],
                depends=["simulation_robomaker"]
            ),
            SequentialStage(
                description="Build final Docker image",
                jobs=["dockerfile_final", "build_final_image"]
            )
        ]
    )
