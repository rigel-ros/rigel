import inspect
import unittest
from rigel.plugins.core.registry_plugin.plugin import Plugin
from rigel.plugins.core.registry_plugin.registries import (
    ECRPlugin,
    GenericDockerRegistryPlugin
)
from unittest.mock import MagicMock, Mock, patch


class PluginTesting(unittest.TestCase):
    """
    Test suite for the rigel.plugins.core.registry_plugin.Plugin class.
    """

    def test_run_compliant(self) -> None:
        """
        Ensure that Plugin class has required 'run' functions.
        """
        self.assertTrue('run' in Plugin.__dict__)

        run_signature = inspect.signature(Plugin.run)
        self.assertEqual(len(run_signature.parameters), 1)

    def test_stop_compliant(self) -> None:
        """
        Ensure that Plugin class has required 'stop' function.
        """
        self.assertTrue('stop' in Plugin.__dict__)

        stop_signature = inspect.signature(Plugin.stop)
        self.assertEqual(len(stop_signature.parameters), 1)

    @patch('rigel.plugins.core.registry_plugin.registries.ecr.DockerClient')
    @patch('rigel.plugins.core.registry_plugin.plugin.ModelBuilder')
    def test_ecr_plugin_choice(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that plugin type rigel.plugins.core.registry_plugin.registries.ECRPlugin
        is selected if 'ecr' is specified.
        """
        plugin = Plugin(*[], **{'registry': 'ecr'})
        self.assertEqual(plugin.plugin_type, ECRPlugin)

    @patch('rigel.plugins.core.registry_plugin.registries.generic.DockerClient')
    @patch('rigel.plugins.core.registry_plugin.plugin.ModelBuilder')
    def test_generic_plugin_choice_gitlab(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that plugin type rigel.plugins.core.registry_plugin.registries.GenericDockerRegistryPlugin
        is selected if 'gitlab' is specified.
        """
        plugin = Plugin(*[], **{'registry': 'gitlab'})
        self.assertEqual(plugin.plugin_type, GenericDockerRegistryPlugin)

    @patch('rigel.plugins.core.registry_plugin.registries.generic.DockerClient')
    @patch('rigel.plugins.core.registry_plugin.plugin.ModelBuilder')
    def test_generic_plugin_choice_dockerhub(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that plugin type rigel.plugins.core.registry_plugin.GenericDockerRegistryPlugin
        is selected if 'dockerhub' is specified.
        """
        plugin = Plugin(*[], **{'registry': 'dockerhub'})
        self.assertEqual(plugin.plugin_type, GenericDockerRegistryPlugin)

    @patch('rigel.plugins.core.registry_plugin.plugin.ModelBuilder')
    def test_plugin_initialization(self, builder_mock: Mock) -> None:
        """
        Ensure that creation of plugin instances works as expected.
        """
        test_args = [1, 2, 3]
        test_kwargs = {'registry': 'test_registry'}

        plugin_instance_mock = MagicMock()
        builder_mock.return_value = plugin_instance_mock

        plugin = Plugin(*test_args, **test_kwargs)
        plugin.run()

        builder_mock.assert_called_once_with(plugin.plugin_type)
        plugin_instance_mock.build.assert_called_once_with(tuple(test_args), test_kwargs)

    @patch('rigel.plugins.core.registry_plugin.plugin.ModelBuilder')
    def test_plugin_run_function_call(self, builder_mock: Mock) -> None:
        """
        Ensure that execution is properly delegated
        to the 'run' function of the selected plugin.
        """
        plugin_mock = MagicMock()

        builder_instance_mock = MagicMock()
        builder_instance_mock.build.return_value = plugin_mock
        builder_mock.return_value = builder_instance_mock

        plugin = Plugin(*[], **{})
        plugin.run()

        plugin_mock.run.assert_called_once()

    @patch('rigel.plugins.core.registry_plugin.plugin.ModelBuilder')
    def test_plugin_stop_function_call(self, builder_mock: Mock) -> None:
        """
        Ensure that execution is properly delegated
        to the 'stop' function of the selected plugin.
        """
        plugin_mock = MagicMock()

        builder_instance_mock = MagicMock()
        builder_instance_mock.build.return_value = plugin_mock
        builder_mock.return_value = builder_instance_mock

        plugin = Plugin(*[], **{})
        plugin.stop()

        plugin_mock.stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
