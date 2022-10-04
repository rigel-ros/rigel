import click
import os

from rigel.cli import (
    PackageCommand,
    PluginCommand,
    WorkspaceCommand
)
from rigel.exceptions import RigelError, RigelfileAlreadyExistsError
from rigel.files import RigelfileCreator
from rigel.loggers import get_logger
from sys import exit


LOGGER = get_logger()


def rigelfile_exists() -> bool:
    """
    Verify if a Rigelfile is present.

    :rtype: bool
    :return: True if a Rigelfile is found at the current directory. False otherwise.
    """
    return os.path.isfile('./Rigelfile')


@click.group()
def cli() -> None:
    """
    Rigel - containerize and deploy your ROS application using Docker
    """
    pass


@click.command()
@click.option('--force', is_flag=True, default=False, help='Write over an existing Rigelfile.')
def init(force: bool) -> None:
    """
    Create an empty Rigelfile.
    """
    try:

        if rigelfile_exists() and not force:
            raise RigelfileAlreadyExistsError()

        rigelfile_creator = RigelfileCreator()
        rigelfile_creator.create()
        LOGGER.info('Rigelfile created with success.')

    except RigelError as err:
        LOGGER.error(err)
        exit(err.code)


# Add commands to CLI
cli.add_command(init)


def main() -> None:
    """
    Rigel application entry point.
    """
    PackageCommand.add_command(cli)
    PluginCommand.add_command(cli)
    WorkspaceCommand.add_command(cli)
    cli()


if __name__ == '__main__':
    main()
