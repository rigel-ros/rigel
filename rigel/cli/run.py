import click
import traceback
from rigel.cli.command import CLICommand
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.plugins.manager import PluginManager
from rigel.ros.manager import WorkspaceManager
from sys import exit

LOGGER = get_logger()


class RunJobCommand(CLICommand):
    """Run a job or sequence of jobs
    """

    def __init__(self, manager: WorkspaceManager) -> None:
        super().__init__(command='run')
        self.manager = manager

    # TODO:
    # - Support list of jobs
    # - Support flag for packages
    @click.command()
    @click.argument('workspace', type=str, nargs=1)
    @click.argument('jobs', type=str, nargs=-1)
    def job(self, workspace: str, jobs: str) -> None:
        """Run a sequence of jobs
        """
        try:

            ws = self.manager.get_ws(workspace)
            for job in jobs:

                plugins = ws.jobs.get(job, None)
                if not plugins:
                    # TODO: implement search within packages.
                    raise RigelError(f"Rigel-ROS workspace '{workspace}' does not supported job '{job}'")

                LOGGER.info(f"Running job '{job}'")
                plugin_manager = PluginManager()
                for plugin in plugins:
                    plugin_instance = plugin_manager.load(plugin)
                    plugin_manager.run((plugin.name, plugin_instance))

        except RigelError as err:
            LOGGER.error(err)
            traceback.print_exc()
            exit(err.code)
