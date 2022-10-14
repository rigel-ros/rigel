import click
from rigel.config import SettingsManager
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.ros import WorkspaceManager
from sys import exit
from .command import CLICommand

LOGGER = get_logger()


class WorkspaceCommand(CLICommand):
    """Manage Rigel-ROS workspaces
    """

    def __init__(self, settings: SettingsManager) -> None:
        super().__init__(command='workspace')
        self.manager = WorkspaceManager(settings)

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

    # TODO: implement this
    # @click.command()
    # @click.argument('path', type=str)
    # def init(self, path: str) -> None:
    #     """Create new Rigel-ROS workspace from pre-existing ROS workspace
    #     """
    #     try:
    #         pass
    #     except RigelError as err:
    #         LOGGER.error(err)
    #         exit(err.code)

    @click.command()
    def list(self) -> None:
        """List existing Rigel-ROS workspaces
        """
        self.manager.list()

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

    # TODO: implement this as an alias
    # @click.command()
    # @click.argument('identifier', type=str)
    # def tty(self, identifier: str) -> None:
    #     """
    #     Open a terminal session inside a Rigel-ROS workspace
    #     """
    #     try:
    #         ROSWorkspace.tty(identifier)
    #     except RigelError as err:
    #         LOGGER.error(err)
    #         exit(err.code)
