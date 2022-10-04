import click
from rigel.ros import ROSWorkspace
from rigelcore.exceptions import RigelError
from rigelcore.loggers import get_logger
from sys import exit

LOGGER = get_logger()


@click.group()
def ws() -> None:
    """
    Manage Rigel-ROS workspaces
    """
    pass


@click.command()
@click.argument('distro', type=str)
@click.argument('identifier', type=str)
def create(distro: str, identifier: str) -> None:
    """
    Create a new Rigel-ROS workspace
    """
    try:
        ROSWorkspace.new(distro, identifier)
    except RigelError as err:
        LOGGER.error(err)
        exit(err.code)


@click.command()
def ls() -> None:
    """
    List existing Rigel-ROS workspaces
    """
    ROSWorkspace.list()


@click.command()
@click.argument('identifier', type=str)
def tty(identifier: str) -> None:
    """
    Open a terminal session inside a Rigel-ROS workspace
    """
    try:
        ROSWorkspace.tty(identifier)
    except RigelError as err:
        LOGGER.error(err)
        exit(err.code)


# Assemble 'ws' command
ws.add_command(create)
ws.add_command(ls)
ws.add_command(tty)


class WorkspaceCommand:

    @staticmethod
    def add_command(group: click.Group) -> None:
        """Registers CLI command 'ws'.

        :group: the top-level CLI 'rigel' command.
        :type: click.Group
        """
        return group.add_command(ws)
