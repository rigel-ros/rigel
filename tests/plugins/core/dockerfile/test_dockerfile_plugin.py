import os
import unittest
from rigel.models.package import Package, SSHKey
from rigel.plugins import Plugin as PluginBase
from rigel.plugins.core.dockerfile.models import PluginModel
from rigel.plugins.core.dockerfile.plugin import Plugin
from typing import Any, Dict
from unittest.mock import call, Mock, patch

TEST_DISTRO = 'test_distro'
TEST_SSH_KEY_ENV = 'STANDARD_SSH_KEY_REGISTRY_ENV'
TEST_SSH_KEY_VALUE = 'dummy-ssh-key'

os.environ[TEST_SSH_KEY_ENV] = TEST_SSH_KEY_VALUE
DUMMY_SSH_MODEL = PluginModel(
    distro=TEST_DISTRO,
    command='test_command',
    package=Package(
        dir='ssh_dir',
        ssh=[SSHKey(hostname='standard_registry', value=TEST_SSH_KEY_ENV)]
    )
)

DUMMY_STANDARD_MODEL = PluginModel(
    distro=TEST_DISTRO,
    command='test_command',
    package=Package(dir='standard_dir')
)


class DockerfileCorePluginTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.core.dockerfile.plugin.Plugin class.
    """

    def get_initial_data(self, model: PluginModel) -> Dict[str, Any]:
        data = model.dict()
        data.pop('distro')
        data.pop('package')
        return data

    ###

    def test_inherits_from_plugin(self) -> None:
        """
        Ensure that entrypoint class inherits
        from rigel.plugins.core.dockerfile.plugin.Plugin class.
        """
        self.assertTrue(issubclass(Plugin, PluginBase))

    @patch('rigel.plugins.core.dockerfile.plugin.Plugin.prepare_targets')
    def test_prepare_targets_called(self, prepare_targets_mock: Mock) -> None:
        """
        Ensure that targets are process during initialization.
        """
        Plugin(TEST_DISTRO, [])
        prepare_targets_mock.assert_called_once()

    @patch('rigel.plugins.core.dockerfile.plugin.Renderer')
    def test_rigelfile_creation(self, renderer_mock: Mock) -> None:
        """
        Test if the creation of a new Rigelfile is done as expected.
        """
        renderer_mock.return_value = renderer_mock

        plugin = Plugin(TEST_DISTRO, [
            ('test_target_0', DUMMY_SSH_MODEL.package, self.get_initial_data(DUMMY_SSH_MODEL)),
            ('test_target_1', DUMMY_STANDARD_MODEL.package, self.get_initial_data(DUMMY_STANDARD_MODEL))
        ])
        plugin.run()

        renderer_constructor_calls = [
            call(DUMMY_SSH_MODEL),
            call.render('Dockerfile.j2', f'{DUMMY_SSH_MODEL.package.dir}/Dockerfile'),
            call.render('entrypoint.j2', f'{DUMMY_SSH_MODEL.package.dir}/dockerfile_entrypoint.sh'),
            call.render('config.j2', f'{DUMMY_SSH_MODEL.package.dir}/dockerfile_config'),
            call(DUMMY_STANDARD_MODEL),
            call.render('Dockerfile.j2', f'{DUMMY_STANDARD_MODEL.package.dir}/Dockerfile'),
            call.render('entrypoint.j2', f'{DUMMY_STANDARD_MODEL.package.dir}/dockerfile_entrypoint.sh'),
        ]
        renderer_mock.assert_has_calls(renderer_constructor_calls)


if __name__ == '__main__':
    unittest.main()
