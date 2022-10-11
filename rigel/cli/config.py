import click
from rigel.config import SettingsManager


@click.group()
def config() -> None:
    """
    Manages Rigel configuration settings
    """
    pass


@click.command()
def list() -> None:
    """
    List active configuration settings
    """
    manager = SettingsManager()
    manager.list_settings()


@click.command()
@click.argument('setting', type=str)
@click.argument('value', type=str)
def set(setting: str, value: str) -> None:
    """
    Set configuration settings
    """
    manager = SettingsManager()
    manager.update_setting(setting, value)


@click.command()
@click.argument('setting', type=str)
def reset(setting: str) -> None:
    """
    Reset configuration settings
    """
    manager = SettingsManager()
    if setting == 'all':
        manager.reset_settings_file()
    else:
        manager.reset_setting(setting)


# Assemble 'config' command
config.add_command(list)
config.add_command(set)
config.add_command(reset)


class ConfigCommand:

    @staticmethod
    def add_command(group: click.Group) -> None:
        """Registers CLI command 'config'.

        :group: the top-level CLI 'rigel' command.
        :type: click.Group
        """
        return group.add_command(config)
