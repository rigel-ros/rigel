import unittest
from pydantic import BaseModel
from rigel.exceptions import (
    PluginNotFoundError,
)
from rigel.models import PluginSection
from rigel.plugins import PluginLoader
from unittest.mock import Mock, patch


class TestPluginWithoutRun(BaseModel):
    pass


class TestPluginInvalidRun(BaseModel):
    def run(self, text: str) -> None:
        pass


class TestPlugin(BaseModel):
    def run(self) -> None:
        pass


class PluginLoaderTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.PluginLoader class.
    """

    def test_plugin_compliant_checker(self) -> None:
        """
        Test if function 'is_plugin_compliant' works as expected.
        """
        loader = PluginLoader()
        self.assertTrue(loader.is_plugin_compliant(TestPlugin))
        self.assertFalse(loader.is_plugin_compliant(TestPluginWithoutRun))

    def test_run_signature_checker(self) -> None:
        """
        Test if function 'is_run_compliant' works as expected.
        """
        loader = PluginLoader()
        self.assertTrue(loader.is_run_compliant(TestPlugin))
        self.assertFalse(loader.is_run_compliant(TestPluginInvalidRun))

    def test_plugin_not_found_error(self) -> None:
        """
        Test if PluginNotFoundError is thrown if an unknown plugin is declared.
        """
        plugin_name = 'user.unknown_plugin'
        plugin_entrypoint = 'TestEntrypoint'
        plugin = PluginSection(**{'name': plugin_name, 'entrypoint': plugin_entrypoint})

        with self.assertRaises(PluginNotFoundError) as context:
            loader = PluginLoader()
            loader.load(plugin)
        self.assertEqual(context.exception.kwargs['plugin'], f'{plugin_name}.{plugin_entrypoint}')

    @patch('rigel.plugins.loader.getattr')
    @patch('rigel.plugins.loader.import_module')
    @patch('rigel.plugins.loader.ModelBuilder.build')
    def test_simulate_plugin_creation(
            self,
            builder_mock: Mock,
            importlib_mock: Mock,
            getattr_mock: Mock
            ) -> None:
        """
        Test if plugins are properly initialized and correctly passed their data.
        """
        plugin_name = 'rigel.test'
        plugin_entrypoint = 'EntrypointClass'
        plugin_args = [1, 2, 3]
        plugin_kwargs = {'test_field': 'test_value'}

        importlib_mock.return_value = 'PluginModule'
        getattr_mock.return_value = TestPlugin
        builder_mock.return_value = 'PluginInstance'

        loader = PluginLoader()
        loader.load(PluginSection(**{
            'name': plugin_name,
            'entrypoint': plugin_entrypoint,
            'args': plugin_args,
            'kwargs': plugin_kwargs
        }))

        importlib_mock.assert_called_once_with(plugin_name)
        getattr_mock.assert_called_once_with('PluginModule', plugin_entrypoint)
        builder_mock.assert_called_with(plugin_args, plugin_kwargs)


if __name__ == '__main__':
    unittest.main()
