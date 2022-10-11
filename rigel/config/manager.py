import os
import yaml
from rigel.loggers import get_logger
from typing import Any
from .defaults import RIGEL_FOLDER, Settings

LOGGER = get_logger()

SETTINGS_FILE_PATH = f'{RIGEL_FOLDER}/config'


class SettingsManager:

    def __init__(self) -> None:

        if not os.path.exists(SETTINGS_FILE_PATH):
            self.settings = self.load_default_settings()
            self.reset_settings_file()
        else:
            self.settings = self.load_settings()

    def load_default_settings(self) -> Settings:
        """Load default application settings.

        :return: Default application settings.
        :rtype: Settings
        """
        return Settings()

    def load_settings(self) -> Settings:
        """Load active application settings from local settings file.

        :return: Active application settings.
        :rtype: Settings
        """
        with open(SETTINGS_FILE_PATH, 'r') as settings_file:
            settings = settings_file.readlines()
        return Settings(**yaml.safe_load(''.join(settings)))

    def update_settings_file(self, settings: Settings) -> None:
        """Create or update local settings file.

        :param settings: The settings to be recorded.
        :type settings: Settings
        """
        with open(SETTINGS_FILE_PATH, 'w+') as settings_file:
            settings_file.write(
                yaml.dump(settings.dict())
            )

    def reset_settings_file(self) -> None:
        """Reset all setting values in local settings file.
        """
        self.settings = self.load_default_settings()
        self.update_settings_file(
            self.load_default_settings()
        )

    def list_settings(self) -> None:
        """Display active application settings.
        """
        LOGGER.info(self.settings)

    def get_setting(self, settings: Settings, setting: str) -> Any:
        """Obtain the value of an individual applicaton setting.

        :param settings: The desired group of settings from which to retrieve the value.
        :type settings: Settings
        :param setting: The setting whose value is to be retrieved.
        :type setting: str
        :return: The setting value
        :rtype: Any
        """
        path = setting.split('.')
        try:
            elem = settings.__getattribute__(path[0])
            for attribute in path[1:]:
                elem = elem.__getattribute__(attribute)
        except AttributeError as err:
            raise err
        return elem

    def update_setting(self, setting: str, value: Any) -> None:
        """Update the value of an individual application setting.

        :param setting: The setting to be updated.
        :type setting: str
        :param value: The new value for the setting.
        :type value: Any
        """
        path = setting.rsplit('.', 1)
        setattr(
            self.get_setting(self.settings, path[0]),
            path[-1],
            value
        )
        self.update_settings_file(self.settings)

    def reset_setting(self, setting: str) -> None:
        """Resets the value of an individual applicaton setting to its default.

        :param setting: The setting to be reseted.
        :type setting: str
        """
        self.update_setting(
            setting,
            self.get_setting(self.load_default_settings(), setting)
        )
