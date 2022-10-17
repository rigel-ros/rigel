import click
import os

from rigel.cli.config import ConfigCommand
from rigel.cli.run import RunJobCommand
from rigel.cli.workspace import WorkspaceCommand

# PackageCommand,
# PluginCommand,
from rigel.config import RIGEL_FOLDER, SettingsManager
from rigel.loggers import get_logger
from rigel.ros.manager import WorkspaceManager


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
    workspace_manager = WorkspaceManager(settings)

    ConfigCommand(settings).add_to_group(cli)
    RunJobCommand(workspace_manager).add_to_group(cli)
    WorkspaceCommand(workspace_manager).add_to_group(cli)

    cli()


if __name__ == '__main__':
    main()
