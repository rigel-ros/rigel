from rigel.files.decoder import YAMLDataDecoder
from rigel.files.loader import YAMLDataLoader
from rigel.models.builder import ModelBuilder
from rigel.models.rigelfile import Rigelfile, Package
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

    def get_package(self, package: str) -> Package:
        """Retrieve a listed ROS package, if existent.

        :param package: The ROS package identifier.
        :type package: str
        :return: The ROS package.
        :rtype: Package
        """
        try:
            return [pkg for pkg in self.workspace.packages if pkg.name == package][0]
        except IndexError:
            raise Exception(f"Package '{package}' was not found")

    def get_sequence_jobs(self, sequence: str) -> List[str]:
        """Retrieve jobs of a given sequence.

        :param sequence: The sequence identifier.
        :type sequence: str
        :return: The list of jobs.
        :rtype: List[str]
        """
        try:
            return self.workspace.sequences[sequence]
        except KeyError:
            raise Exception(f"Sequence '{sequence}' was not found")

    def run_sequence(self, sequences: List[str], package: Optional[str] = None) -> None:
        """Run a single sequence or a list of job sequences.

        :param sequences: A list of sequence identifiers.
        :type sequences: List[str]
        :param package:, defaults to None
        :type package: Optional[str], optional
        :raises Exception: _description_
        """
        for sequence in sequences:
            self.run_jobs(self.get_sequence_jobs(sequence), package)

    def run_jobs(self, jobs: List[str], package: Optional[str] = None) -> None:
        """Run a single job or a list of jobs.

        :param jobs: A list of job identifiers.
        :type jobs: List[str]
        :param package: The package identifier, default to None.
        When None, the list of jobs are run over all packages.
        :type package: Optional[str]
        """
        if package:
            self.run_jobs_package(jobs, self.get_package(package))
        else:
            for package in self.workspace.packages:
                self.run_jobs_package(jobs, package)

    def run_jobs_package(self, jobs: List[str], package: Package) -> None:
        """Run a list of jobs over a single package.

        :param jobs: A list of job identifiers.
        :type jobs: List[str]
        :param package: The package.
        :type package: Package
        """
        for job in jobs:

            plugins = package.jobs.get(job, None)
            if not plugins:
                raise Exception(f"Package '{package}' does not support job '{job}'")

            for plugin in plugins:
                PluginManager.run(PluginManager.load(self.workspace.distro, package, plugin))
