import sys
from rigel.exceptions import (
    InvalidPluginNameError,
    PluginInstallationError
)
from subprocess import CalledProcessError, check_call


class PluginInstaller:
    """
    A class to install external plugins from both public and private sources.
    """

    def __init__(self, plugin: str, host: str, private: bool) -> None:
        """
        :type plugin: string
        :param plugin: The name of the plugin to install. Each plugin name must follow the format <USERNAME>/<PACKAGE>.
        :type host: string
        :param host: Where the plugin is being hosted.
        :type private: bool
        :param private: When set to True, the plugin is downloaded using SSH.
        When set to False, HTTPS is used instead.
        """
        self.plugin = plugin
        try:
            self.plugin_user, self.plugin_name = plugin.strip().split('/')
        except ValueError:
            raise InvalidPluginNameError(plugin=plugin)
        self.host = host
        self.protocol = 'ssh' if private else 'https'

    def install(self) -> None:
        """
        Install an external plugin.
        """
        url = f"{self.protocol}://{'git@' if self.protocol == 'ssh' else ''}{self.host}/{self.plugin_user}/{self.plugin_name}"

        try:
            check_call([sys.executable, '-m', 'pip', 'install', f'git+{url}'])
        except CalledProcessError:
            raise PluginInstallationError(plugin=self.plugin)
