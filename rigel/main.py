import click
import shutil
from pkg_resources import resource_filename
from rigel.cli.run import RunJobCommand
from rigel.loggers import get_logger


LOGGER = get_logger()


@click.group()
def cli() -> None:
    """
    Rigel - develop your ROS application using Docker
    """
    pass


@click.command()
def init() -> None:
    """
    Create a new Rigelfile.
    """
    # TODO: add Rigelfile detection and add flag to --force
    rigelfile_path = resource_filename(__name__, 'assets/Rigelfile')
    shutil.copyfile(rigelfile_path, 'Rigelfile')
    LOGGER.info("""
    A Rigelfile has been placed in this directory.
    Please read the comments in the Rigelfile
    as well as documentation for more information on using Rigel.
    """)


def main() -> None:
    """
    Rigel application entry point.
    """
    RunJobCommand().add_to_group(cli)

    cli.add_command(init)
    cli()


if __name__ == '__main__':
    main()
