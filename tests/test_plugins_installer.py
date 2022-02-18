import sys
import unittest
from rigel.exceptions import (
    InvalidPluginName,
    PluginInstallationError
)
from rigel.plugins import PluginInstaller
from subprocess import CalledProcessError
from unittest.mock import Mock, patch


class PluginInstallerTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.PluginInstaller class.
    """

    def test_invalid_plugin_name_error(self) -> None:
        """
        Test if InvalidPluginName is thrown if an invalid plugin name is provided.
        """
        invalid_plugin_name = 'invalid_plugin_name'
        with self.assertRaises(InvalidPluginName) as context:
            installer = PluginInstaller(invalid_plugin_name, 'github.com', False)
            installer.install()
        self.assertEqual(context.exception.kwargs['plugin'], 'invalid_plugin_name')

    @patch('rigel.plugins.installer.check_call')
    def test_plugin_name_parts(self, subprocess_mock: Mock) -> None:
        """
        Test if valid plugin names' parts are properly extracted.
        """
        plugin_user = 'test_user'
        plugin_name = 'test_plugin'
        plugin = f'{plugin_user}/{plugin_name}'
        installer = PluginInstaller(plugin, 'github.com', False)
        self.assertEqual(installer.plugin, plugin)
        self.assertEqual(installer.plugin_user, plugin_user)
        self.assertEqual(installer.plugin_name, plugin_name)

    @patch('rigel.plugins.installer.check_call')
    def test_check_protocol_private(self, subprocess_mock: Mock) -> None:
        """
        Test if SSH protocol is used whenever a private package is selected.
        """
        plugin_user = 'test_user'
        plugin_name = 'test_plugin'
        plugin = f'{plugin_user}/{plugin_name}'
        installer = PluginInstaller(plugin, 'github.com', True)
        self.assertEqual(installer.protocol, 'ssh')

    @patch('rigel.plugins.installer.check_call')
    def test_check_protocol_public(self, subprocess_mock: Mock) -> None:
        """
        Test if HTTPS protocol is used whenever a public package is selected.
        """
        plugin_user = 'test_user'
        plugin_name = 'test_plugin'
        plugin = f'{plugin_user}/{plugin_name}'
        installer = PluginInstaller(plugin, 'github.com', False)
        self.assertEqual(installer.protocol, 'https')

    @patch('rigel.plugins.installer.check_call')
    def test_check_subprocess_call_https(self, subprocess_mock: Mock) -> None:
        """
        Test if Pip is called with the correct arguments when using HTTPS.
        """
        plugin_user = 'test_user'
        plugin_name = 'test_plugin'
        plugin = f'{plugin_user}/{plugin_name}'
        host = 'test_host'
        installer = PluginInstaller(plugin, host, False)
        installer.install()

        url = f"{installer.protocol}://{host}/{plugin_user}/{plugin_name}"
        subprocess_mock.assert_called_once_with([sys.executable, '-m', 'pip', 'install', f'git+{url}'])

    @patch('rigel.plugins.installer.check_call')
    def test_check_subprocess_call_ssh(self, subprocess_mock: Mock) -> None:
        """
        Test if Pip is called with the correct arguments when using SSH.
        """
        plugin_user = 'test_user'
        plugin_name = 'test_plugin'
        plugin = f'{plugin_user}/{plugin_name}'
        host = 'test_host'
        installer = PluginInstaller(plugin, host, True)
        installer.install()

        url = f"{installer.protocol}://git@{host}/{plugin_user}/{plugin_name}"
        subprocess_mock.assert_called_once_with([sys.executable, '-m', 'pip', 'install', f'git+{url}'])

    @patch('rigel.plugins.installer.check_call')
    def test_plugin_installation_error(self, subprocess_mock: Mock) -> None:
        """
        Test if PluginInstallationError is thrown  with the correct arguments.
        """
        plugin_user = 'test_user'
        plugin_name = 'test_plugin'
        plugin = f'{plugin_user}/{plugin_name}'

        subprocess_mock.return_value = None
        subprocess_mock.side_effect = CalledProcessError(404, 'test_command')

        with self.assertRaises(PluginInstallationError) as context:
            installer = PluginInstaller(plugin, 'github.com', False)
            installer.install()
        self.assertEqual(context.exception.kwargs['plugin'], plugin)


if __name__ == '__main__':
    unittest.main()
