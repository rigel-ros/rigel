import click
from rigel.config import SettingsManager
from .command import CLICommand


class ConfigCommand(CLICommand):
    """Manages Rigel configuration settings
    """

    def __init__(self, settings: SettingsManager) -> None:
        super().__init__(command='config')
        self.manager = settings

    @click.command()
    def list(self) -> None:
        """
        List active configuration settings
        """
        self.manager.list_settings()

    @click.command()
    @click.argument('setting', type=str)
    @click.argument('value', type=str)
    def set(self, setting: str, value: str) -> None:
        """
        Set configuration settings
        """
        manager = SettingsManager()
        manager.update_setting(setting, value)

    @click.command()
    @click.argument('setting', type=str)
    def reset(self, setting: str) -> None:
        """
        Reset configuration settings
        """
        manager = SettingsManager()
        if setting == 'all':
            manager.reset_settings_file()
        else:
            manager.reset_setting(setting)
