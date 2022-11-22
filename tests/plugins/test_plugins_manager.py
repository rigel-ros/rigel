import unittest
from pydantic import BaseModel
from rigel.exceptions import (
    PluginNotFoundError,
    PluginNotCompliantError,
    RigelError
)
from rigel.models.package import Package, Target
from rigel.plugins.manager import PluginManager
from rigel.plugins.plugin import Plugin
from typing import List
from unittest.mock import MagicMock, Mock, patch


class InvalidPlugin(BaseModel):
    pass


class ValidPlugin(Plugin):

    test_arg: str

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)


class PluginManagerTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.manager.PluginManager class.
    """

    def test_plugin_compliant_checker(self) -> None:
        """
        Test if function 'is_plugin_compliant' works as expected.
        """
        manager = PluginManager()
        self.assertTrue(manager.is_plugin_compliant(ValidPlugin))
        self.assertFalse(manager.is_plugin_compliant(InvalidPlugin))

    def test_plugin_not_found_error(self) -> None:
        """
        Test if an instance of PluginNotFoundError is thrown if an unknown plugin is declared.
        """
        test_plugin_entrypoint = 'rigel.invalid.InvalidPluginEntrypoint'

        with self.assertRaises(PluginNotFoundError) as context:
            manager = PluginManager()
            manager.load(test_plugin_entrypoint, 'distro', [])
        self.assertEqual(context.exception.plugin, test_plugin_entrypoint)

    @patch('rigel.plugins.manager.getattr')
    @patch('rigel.plugins.manager.import_module')
    def test_plugin_not_compliant_error(self, import_mock: Mock, getattr_mock: Mock) -> None:
        """
        Test if an instance of PluginNotCompliantError is thrown if plugin is declared that does not
        inherit from class rigel.plugins.plugin.Plugin .
        """

        test_plugin_entrypoint = '   rigel.invalid.InvalidPluginEntrypoint   '.strip()
        test_plugin_name, _ = test_plugin_entrypoint.rsplit('.', 1)

        module_mock = MagicMock()
        import_mock.return_value = module_mock

        getattr_mock.return_value = InvalidPlugin

        with self.assertRaises(PluginNotCompliantError) as context:
            manager = PluginManager()
            manager.load(test_plugin_entrypoint, 'distro', [])

        import_mock.assert_called_once_with(test_plugin_name)
        self.assertEqual(context.exception.plugin, test_plugin_entrypoint)

    @patch('rigel.plugins.manager.getattr')
    @patch('rigel.plugins.manager.import_module')
    def test_plugin_loading(
            self,
            import_mock: Mock,
            getattr_mock: Mock
            ) -> None:
        """
        Test if plugins are properly initialized and correctly passed their respective data.
        """
        test_plugin_entrypoint = '   rigel.invalid.InvalidPluginEntrypoint   '.strip()
        test_plugin_name, _ = test_plugin_entrypoint.rsplit('.', 1)

        test_distro = 'test_distro'
        test_targets = [('test_target_pkg', Package(), {'test_key': 'test_value'})]

        module_mock = MagicMock()
        import_mock.return_value = module_mock
        getattr_mock.return_value = ValidPlugin

        manager = PluginManager()
        plugin = manager.load(test_plugin_entrypoint, test_distro, test_targets)

        import_mock.assert_called_once_with(test_plugin_name)
        self.assertEqual(plugin.distro, test_distro)
        self.assertEqual(plugin.targets, test_targets)

    def test_plugin_run(self) -> None:
        """Test if the the execution flow of plugins works as expected.
        """
        plugin = MagicMock()

        manager = PluginManager()
        manager.run(plugin)

        plugin.__enter__.assert_called_once()
        plugin.run.assert_called_once()
        plugin.__exit__.assert_called_once()

    @patch('rigel.plugins.manager.sys.exit')
    def test_plugin_run_error(self, exit_mock: Mock) -> None:
        """Test if the the execution flow of plugins works as expected
            whenever there's an execution error.
        """
        plugin = MagicMock()
        plugin.run.side_effect = RigelError()

        manager = PluginManager()
        manager.run(plugin)

        plugin.__enter__.assert_called_once()
        plugin.run.assert_called_once()
        plugin.stop.assert_called_once()

        exit_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
