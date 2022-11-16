import click
import os
import shutil
from pkg_resources import resource_filename
from rigel.cli.run import RunJobCommand
from rigel.loggers import get_logger


LOGGER = get_logger()


@click.group()
def cli() -> None:
    """
    Rigel - automate your ROS pipelines using containers.
    """
    pass


@click.command()
@click.option('--force', 'force', type=bool, is_flag=True, help='Overwrite existing Rigelfile')
def init(force: bool) -> None:
    """
    Create a new Rigelfile.
    """

    if os.path.exists('./Rigelfile') and not force:
        LOGGER.info("""
        A Rigelfile already exists in this directory.
        To overwrite it with a new one rerun this command with the --force flag.
        """)

    else:
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
