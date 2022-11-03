from rigel.files.decoder import YAMLDataDecoder
from rigel.files.loader import YAMLDataLoader
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.package import Target
from rigel.models.plugin import PluginSection
from rigel.models.rigelfile import Rigelfile
from rigel.plugins.manager import PluginManager
from typing import List, Tuple


LOGGER = get_logger()


class WorkspaceManager:

    def __init__(self, path: str) -> None:
        """Class constructor.
        Retrieve workspace information from a Rigelfile.

        :path: path to Rigelfile.
        :type: str
        """
        loader = YAMLDataLoader(path)
        decoder = YAMLDataDecoder()
        yaml_data = decoder.decode(loader.load())

        self.workspace = ModelBuilder(Rigelfile).build([], yaml_data)

    def get_job_data(self, job: str) -> Tuple[str, PluginSection]:
        """Retrieve a listed job, if existent.

        :param job: The job identifier.
        :type job: str
        :return: The job information.
        :rtype: PluginSection
        """
        try:
            return job, self.workspace.jobs[job]
        except KeyError:
            raise Exception(f"Job '{job}' was not found")

    def get_sequence_data(self, sequence: str) -> List[str]:
        """Retrieve a sequence of jobs, if existent.

        :param sequence: The sequence identifier.
        :type sequence: str
        :return: The sequence of jobs.
        :rtype: List[str]
        """
        try:
            return self.workspace.sequences[sequence]
        except KeyError:
            raise Exception(f"Sequence '{sequence}' was not found")

    def get_target_packages(self, job: Tuple[str, PluginSection]) -> List[Target]:
        """Obtain information about the targets of a given job.

        :param job: A tuple containing the job identifier and global job information.
        :type job: Tuple[str, PluginSection]
        :return: A list of targets.
        :rtype: List[Target]
        """

        job_identifier, job_data = job
        targets = job_data.targets

        if isinstance(targets, str):

            if targets == 'all':

                return [
                    (name, data, data.jobs[job_identifier]) for name, data in self.workspace.packages.items()
                    if data.jobs.get(job_identifier)
                ]

            else:

                return [
                    (name, data, data.jobs[job_identifier]) for name, data in self.workspace.packages.items()
                    if data.jobs.get(job_identifier) and name == targets
                ]

        # else:  # a list of targets was provided
        return [
            (name, data, data.jobs[job_identifier]) for name, data in self.workspace.packages.items()
            if data.jobs.get(job_identifier) and name in targets
        ]

    def execute_job(self, job: Tuple[str, PluginSection]) -> None:
        """Execute a single job.

        :param job: A tuple containing the job identifier and global job information.
        :type job: Tuple[str, PluginSection]
        """
        job_identifier, job_data = job
        targets = self.get_target_packages(job)
        if not targets:
            LOGGER.warning(f"No target package was found for job '{job_identifier}'.")
        else:
            manager = PluginManager()
            plugin = manager.load(job_data.plugin, self.workspace.distro, targets)
            manager.run(plugin)

    def run_job(self, job: str) -> None:
        """Run a single job.

        :param sequence: The job identifier.
        :type sequence: str
        """
        self.execute_job(self.get_job_data(job))

    def run_sequence(self, sequence: str) -> None:
        """Run a sequence of jobs.

        :param sequence: The sequence identifier.
        :type sequence: str
        """
        jobs = [self.get_job_data(job) for job in self.get_sequence_data(sequence)]
        for job in jobs:
            self.execute_job(job)


if __name__ == '__main__':

    manager = WorkspaceManager('./Rigelfile')
    print(manager.workspace)
