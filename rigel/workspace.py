from rigel.files.decoder import YAMLDataDecoder
from rigel.files.loader import YAMLDataLoader
from rigel.models.builder import ModelBuilder
from rigel.models.rigelfile import Rigelfile
from rigel.plugins.manager import PluginManager
from typing import List, Optional


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

    def run_sequence(self, sequences: List[str], package: Optional[str] = None) -> None:
        """Run a single sequence or a list of job sequences.

        :param sequences: A list of sequence identifiers.
        :type sequences: List[str]
        :param package:, defaults to None
        :type package: Optional[str], optional
        :raises Exception: _description_
        """
        for sequence in sequences:

            jobs = self.workspace.sequences.get(sequence, None)
            if not jobs:
                raise Exception(f"Sequence '{sequence}' was not found")

            if package:
                self.run_sequence_package(jobs, package)
            else:
                for package in self.workspace.packages.keys():
                    self.run_sequence_package(jobs, package)

    def run_jobs(self, jobs: List[str], package: Optional[str] = None) -> None:
        """Run a single job or a list of jobs.

        :param jobs: A list of job identifiers.
        :type jobs: List[str]
        :param package: The package identifier, default to None.
        When None, the list of jobs are run over all packages.
        :type package: Optional[str]
        """
        if package:
            self.run_jobs_package(jobs, package)
        else:
            for package in self.workspace.packages.keys():
                self.run_jobs_package(jobs, package)

    def run_jobs_package(self, jobs: List[str], package: str) -> None:
        """Run a list of jobs over a single package.

        :param jobs: A list of job identifiers.
        :type jobs: List[str]
        :param package: The package identifier.
        :type package: str
        """
        package_instance = self.workspace.packages.get(package, None)
        if not package_instance:
            raise Exception(f"Package '{package}' was not found")

        for job in jobs:

            plugins = package_instance.jobs.get(job, None)
            if not plugins:
                raise Exception(f"Package '{package}' does not support job '{job}'")

            for plugin in plugins:
                PluginManager.run(PluginManager.load(plugin))
