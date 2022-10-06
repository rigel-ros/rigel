import unittest
from rigel.plugins.core.registry_plugin.registries.generic import GenericDockerRegistryPlugin
from rigel.exceptions import UndeclaredEnvironmentVariableError
from unittest.mock import Mock, patch


class GenericDockerRegistryPluginTesting(unittest.TestCase):
    """
    Test suite for the rigel_registry_plugin.registries.GenericDockerRegistryPlugin class.
    """

    base_plugin_data = {
        'credentials': {
            'username': 'TEST_USERNAME',
            'password': 'TEST_PASSWORD'
        },
        'image': 'test_image',
        'local_image': 'test_local_image',
        'registry': 'test_registry',

    }

    @patch('rigel.plugins.core.registry_plugin.registries.generic.DockerClient')
    def test_tag_call(self, docker_mock: Mock) -> None:
        """
        Test if function 'tag' interfaces as expected with rigel.clients.DockerClient.
        """
        client_mock = Mock()
        docker_mock.return_value = client_mock

        plugin = GenericDockerRegistryPlugin(*[], **self.base_plugin_data)
        plugin.tag()
        client_mock.tag_image.assert_called_once_with(
            self.base_plugin_data['local_image'],
            f"{self.base_plugin_data['registry']}/{self.base_plugin_data['image']}"
        )

    @patch('rigel.plugins.core.registry_plugin.registries.generic.os.environ.get')
    def test_undeclared_environment_variable_error(self, environ_mock: Mock) -> None:
        """
        Test if UndeclaredEnvironmentVariableError is thrown
        if an environment variable was left undeclared.
        """
        test_username = 'test_username'
        test_environ = {'TEST_USERNAME': test_username}

        environ_mock.side_effect = test_environ.get

        with self.assertRaises(UndeclaredEnvironmentVariableError) as context:
            plugin = GenericDockerRegistryPlugin(*[], **self.base_plugin_data)
            plugin.authenticate()

        self.assertEqual(context.exception.kwargs['env'], 'TEST_PASSWORD')

    @patch('rigel.plugins.core.registry_plugin.registries.generic.os.environ.get')
    @patch('rigel.plugins.core.registry_plugin.registries.generic.DockerClient')
    def test_authenticate_call(self, docker_mock: Mock, environ_mock: Mock) -> None:
        """
        Test if function 'authenticate' interfaces as expected
        with rigel.clients.DockerClient class.
        """

        client_mock = Mock()
        docker_mock.return_value = client_mock

        test_username = 'test_username'
        test_password = 'test_password'
        test_environ = {'TEST_USERNAME': test_username, 'TEST_PASSWORD': test_password}
        environ_mock.side_effect = test_environ.get

        plugin = GenericDockerRegistryPlugin(*[], **self.base_plugin_data)
        plugin.authenticate()
        client_mock.login.assert_called_once_with(
            self.base_plugin_data['registry'],
            test_username,
            test_password
        )

    @patch('rigel.plugins.core.registry_plugin.registries.generic.DockerClient')
    def test_push_call(self, docker_mock: Mock) -> None:
        """
        Test if function 'deploy' interfaces as expected with rigel.clients.DockerClient.
        """

        client_mock = Mock()
        docker_mock.return_value = client_mock

        plugin = GenericDockerRegistryPlugin(*[], **self.base_plugin_data)
        plugin.deploy()
        client_mock.push_image.assert_called_once_with(
            f"{self.base_plugin_data['registry']}/{self.base_plugin_data['image']}"
        )


if __name__ == '__main__':
    unittest.main()
