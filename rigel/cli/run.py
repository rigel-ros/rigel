import click
from rigel.cli.command import CLICommand
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.workspace import WorkspaceManager
from sys import exit

LOGGER = get_logger()


class RunJobCommand(CLICommand):
    """Run a job or sequence of jobs
    """

    def __init__(self) -> None:
        super().__init__(command='run')

    @click.command()
    @click.argument('job', type=str)
    def job(self, job: str) -> None:
        """Run a single job
        """
        try:
            manager = WorkspaceManager('./Rigelfile')
            manager.run_job(job)
        except RigelError as err:
            LOGGER.error(err)
            exit(1)

    @click.command()
    @click.argument('sequence', type=str)
    def sequence(self, sequence: str) -> None:
        """Run a sequence of jobs
        """
        try:
            manager = WorkspaceManager('./Rigelfile')
            manager.run_sequence(sequence)
        except RigelError as err:
            LOGGER.error(err)
            exit(1)
