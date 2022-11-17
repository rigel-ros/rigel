import unittest
from rigel.plugins.plugin import Plugin
from unittest.mock import call, Mock, patch


class PluginBaseTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.Plugin class.
    """

    @patch('rigel.plugins.plugin.Plugin.setup')
    @patch('rigel.plugins.plugin.Plugin.stop')
    @patch('rigel.plugins.plugin.Plugin.handle_signals')
    def test_plugin_context_manager(self, signal_mock: Mock, stop_mock: Mock, setup_mock: Mock) -> None:
        """
        Test if functions __enter__ and __exit__ work as expected.
        """
        plugin = Plugin('distro', [])
        with plugin as instance:
            self.assertEqual(plugin, instance)
            signal_mock.assert_called_once()
            setup_mock.assert_called_once()
        stop_mock.assert_called_once_with()

    @patch('rigel.plugins.plugin.signal')
    def test_plugin_handle_signals(self, signal_mock: Mock) -> None:
        """
        Test if function handle_signals works as expected.
        """
        test_sigint_value = 1
        test_sigtstp_value = 2
        signal_mock.SIGINT = test_sigint_value
        signal_mock.SIGTSTP = test_sigtstp_value

        plugin = Plugin('distro', [])
        plugin.handle_signals()

        calls = [
            call(test_sigint_value, plugin.stop_plugin),
            call(test_sigtstp_value, plugin.stop_plugin)
        ]
        signal_mock.signal.assert_has_calls(calls)

    @patch('rigel.plugins.plugin.exit')
    def test_plugin_exit_called(self, exit_mock: Mock) -> None:
        """
        Test if function stop_plugin calls __exit__ as expected.
        """
        plugin = Plugin('distro', [])
        plugin.stop_plugin()
        exit_mock.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
