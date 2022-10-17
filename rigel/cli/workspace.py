import click
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.ros.manager import WorkspaceManager
from sys import exit
from .command import CLICommand

LOGGER = get_logger()


class WorkspaceCommand(CLICommand):
    """Manage Rigel-ROS workspaces
    """

    def __init__(self, manager: WorkspaceManager) -> None:
        super().__init__(command='workspace')
        self.manager = manager

    @click.command()
    @click.argument('distro', type=str)
    @click.argument('name', type=str)
    def create(self, distro: str, name: str) -> None:
        """Create a new Rigel-ROS workspace
        """
        try:
            self.manager.generate_ws(distro, name)
        except RigelError as err:
            LOGGER.error(err)
            exit(err.code)

    @click.command()
    def list(self) -> None:
        """List existing Rigel-ROS workspaces
        """
        self.manager.list()

    @click.command()
    @click.argument('name', type=str)
    def info(self, name: str) -> None:
        """Display detailed information on a Rigel-ROS workspace.
        """
        try:
            workspace = self.manager.get_ws(name)
            LOGGER.info(workspace)
        except RigelError as err:
            LOGGER.error(err)
            exit(err.code)

    @click.command()
    @click.argument('name', type=str)
    def path(self, name: str) -> None:
        """Display the system path of a Rigel-ROS workspace
        """
        try:
            path = self.manager.path(name)
            print(path)
        except RigelError as err:
            LOGGER.error(err)
            exit(err.code)
