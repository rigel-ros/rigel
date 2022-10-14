import click
import os

from rigel.cli.config import ConfigCommand
from rigel.cli.workspace import WorkspaceCommand

# PackageCommand,
# PluginCommand,
from rigel.config import RIGEL_FOLDER, SettingsManager
from rigel.loggers import get_logger


LOGGER = get_logger()


@click.group()
def cli() -> None:
    """
    Rigel - containerize and deploy your ROS application using Docker
    """
    pass


def main() -> None:
    """
    Rigel application entry point.
    """

    # Ensure that Rigel folder is always created
    if not os.path.exists(RIGEL_FOLDER):
        os.makedirs(RIGEL_FOLDER)

    settings = SettingsManager()

    ConfigCommand(settings).add_to_group(cli)
    # PackageCommand.add_command(cli)
    # PluginCommand.add_command(cli)
    WorkspaceCommand(settings).add_to_group(cli)

    cli()


if __name__ == '__main__':
    main()
