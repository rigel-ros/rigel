import click
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.plugins import PluginInstaller
from sys import exit

LOGGER = get_logger()


@click.group()
def plugin() -> None:
    """
    Manage Rigel plugins
    """
    pass


@click.command()
@click.argument('plugin', type=str)
@click.option('--host', default='github.com', help="URL of the hosting platform. Default is 'github.com'.")
@click.option('--ssh', is_flag=True, default=False, help='Whether the plugin is public or private. Use flag when private.')
def install(plugin: str, host: str, ssh: bool) -> None:
    """
    Install external Rigel plugins.
    """
    try:
        installer = PluginInstaller(plugin, host, ssh)
        installer.install()
    except RigelError as err:
        LOGGER.error(err)
        exit(err.code)


# Assemble 'plugin' command
plugin.add_command(install)


class PluginCommand:

    @staticmethod
    def add_command(group: click.Group) -> None:
        """Registers CLI command 'package'.

        :group: the top-level CLI 'rigel' command.
        :type: click.Group
        """
        return group.add_command(plugin)
