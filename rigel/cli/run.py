import click
from rigel.cli.command import CLICommand
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.workspace import WorkspaceManager
from sys import exit
from typing import Optional, Tuple

LOGGER = get_logger()


class RunJobCommand(CLICommand):
    """Run a job or sequence of jobs
    """

    def __init__(self) -> None:
        super().__init__(command='run')

    @click.command()
    @click.argument('jobs', type=str, nargs=-1)
    @click.option('-p', '--pkg', 'package', type=str, default=None)
    def job(self, jobs: Tuple[str], package: Optional[str]) -> None:
        """Run multiple jobs
        """
        manager = WorkspaceManager('./Rigelfile')
        try:
            manager.run_jobs(list(jobs), package)
        except RigelError as err:
            LOGGER.error(err)
            exit(err.code)

    @click.command()
    @click.argument('sequences', type=str, nargs=-1)
    @click.option('-p', '--pkg', 'package', default=None)
    def sequence(self, sequences: Tuple[str], package: Optional[str]) -> None:
        """Run multiple job sequences
        """
        manager = WorkspaceManager('./Rigelfile')
        try:
            manager.run_sequence(list(sequences), package)
        except RigelError as err:
            LOGGER.error(err)
            exit(err.code)
