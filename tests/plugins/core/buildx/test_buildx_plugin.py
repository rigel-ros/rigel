import os
import unittest
from python_on_whales.exceptions import DockerException
from rigel.exceptions import DockerAPIError
from rigel.models.application import (
    Package,
    ElasticContainerRegistry,
    StandardContainerRegistry,
    SSHKey
)
from rigel.plugins import Plugin as PluginBase
from rigel.plugins.core.buildx.models import PluginModel
from rigel.plugins.core.buildx.plugin import Plugin
from typing import Any, Dict
from unittest.mock import call, Mock, patch


TEST_DISTRO = 'test_distro'

DUMMY_STANDARD_REGISTRY = StandardContainerRegistry(
    type='standard',
    server='test_server',
    password='text_password',
    username='text_username'
)

DUMMY_ECR = ElasticContainerRegistry(
    type='ecr',
    server='test_server',
    aws_access_key_id='test_aws_access_key_id',
    aws_secret_access_key='test_aws_secret_access_key',
    region_name='test_region_name'
)

DUMMY_NO_REGISTRY_MODEL = PluginModel(
    distro=TEST_DISTRO,
    image='test_image',
    package=Package()
)

os.environ['STANDARD_REGISTRY_ENV'] = 'test-standard-registry-url'
DUMMY_STANDARD_MODEL = PluginModel(
    distro=TEST_DISTRO,
    image='test_image',
    package=Package(
        dir='standard_dir',
        ssh=[SSHKey(hostname='standard_registry', value='STANDARD_REGISTRY_ENV')],
        registries=[DUMMY_STANDARD_REGISTRY]
    ),
    buildargs={'TEST': 'STANDARD'},
    load=True
)

DUMMY_ECR_MODEL = PluginModel(
    distro=TEST_DISTRO,
    image='test_image',
    package=Package(
        dir='ecr_dir',
        registries=[DUMMY_ECR]
    ),
    buildargs={'TEST': 'ECR'},
    platforms=['linux/arm64'],
    push=True
)

TEST_BUILDER_NAME = 'test_builder_name'


@patch('rigel.plugins.core.buildx.plugin.BUILDX_BUILDER_NAME', TEST_BUILDER_NAME)
class BuildXPluginTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.core.buildx.plugin.Plugin class.
    """

    def get_initial_data(self, model: PluginModel) -> Dict[str, Any]:
        data = model.dict()
        data.pop('distro')
        data.pop('package')
        return data

    #####

    def test_inherits_from_plugin(self) -> None:
        """
        Ensure that entrypoint class inherits from rigel.plugins.plugin.Plugin class.
        """
        self.assertTrue(issubclass(Plugin, PluginBase))

    @patch('rigel.plugins.core.buildx.plugin.Plugin.prepare_targets')
    def test_prepare_targets_called(self, prepare_targets_mock: Mock) -> None:
        """
        Ensure that targets are process during initialization.
        """
        Plugin(TEST_DISTRO, [])
        prepare_targets_mock.assert_called_once()

    @patch('rigel.plugins.core.buildx.plugin.Plugin.login_standard')
    @patch('rigel.plugins.core.buildx.plugin.Plugin.login_ecr')
    def test_login_dispatch_mechanism_selection_standard(self, ecr_mock: Mock, standard_mock: Mock) -> None:
        """
        Ensure that the adequate login mechanism for standard registries is selected.
        """
        plugin = Plugin(TEST_DISTRO, [])
        plugin.login(DUMMY_STANDARD_REGISTRY)
        standard_mock.assert_called_once_with(DUMMY_STANDARD_REGISTRY)
        ecr_mock.assert_not_called()

    @patch('rigel.plugins.core.buildx.plugin.Plugin.login_standard')
    @patch('rigel.plugins.core.buildx.plugin.Plugin.login_ecr')
    def test_login_dispatch_mechanism_selection_ecr(self, ecr_mock: Mock, standard_mock: Mock) -> None:
        """
        Ensure that the adequate login mechanism for ECR registries is selected.
        """
        plugin = Plugin(TEST_DISTRO, [])
        plugin.login(DUMMY_ECR)
        standard_mock.assert_not_called()
        ecr_mock.assert_called_once_with(DUMMY_ECR)

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_login_standard(self, docker_mock: Mock) -> None:
        """
        Ensure that the login mechanism for standard registries works as expected.
        """
        docker_mock.return_value = docker_mock

        registry = DUMMY_STANDARD_MODEL.package.registries[0]
        assert isinstance(registry, StandardContainerRegistry)

        plugin = Plugin(TEST_DISTRO, [])
        plugin.login(DUMMY_STANDARD_REGISTRY)
        docker_mock.login.assert_called_once_with(
            username=registry.username,
            password=registry.password,
            server=registry.server
        )

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_login_standard_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown if an error occurs during standard login.
        """
        docker_mock.return_value = docker_mock

        test_exception = DockerException(['test_login_command'], 0)
        docker_mock.login.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            plugin = Plugin(TEST_DISTRO, [])
            plugin.login(DUMMY_STANDARD_REGISTRY)

        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_login_ecr(self, docker_mock: Mock) -> None:
        """
        Ensure that the login mechanism for ECR registries works as expected.
        """
        docker_mock.return_value = docker_mock

        registry = DUMMY_ECR_MODEL.package.registries[0]
        assert isinstance(registry, ElasticContainerRegistry)

        plugin = Plugin(TEST_DISTRO, [])
        plugin.login(DUMMY_ECR)
        docker_mock.login_ecr.assert_called_once_with(
            aws_access_key_id=registry.aws_access_key_id,
            aws_secret_access_key=registry.aws_secret_access_key,
            region_name=registry.region_name,
            registry=registry.server
        )

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_login_ecr_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown if an error occurs during AWS login.
        """
        docker_mock.return_value = docker_mock

        test_exception = DockerException(['test_login_command'], 0)
        docker_mock.login_ecr.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            plugin = Plugin(TEST_DISTRO, [])
            plugin.login(DUMMY_ECR)

        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_logout(self, docker_mock: Mock) -> None:
        """
        Ensure that the logout mechanism works as expected.
        """
        docker_mock.return_value = docker_mock

        registry = DUMMY_ECR_MODEL.package.registries[0]
        assert isinstance(registry, ElasticContainerRegistry)

        plugin = Plugin(TEST_DISTRO, [])
        plugin.logout(DUMMY_ECR)
        docker_mock.logout.assert_called_once_with(registry.server)

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_logout_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown if an error occurs during logout.
        """
        docker_mock.return_value = docker_mock

        test_exception = DockerException(['test_login_command'], 0)
        docker_mock.logout.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            plugin = Plugin(TEST_DISTRO, [])
            plugin.logout(DUMMY_ECR)

        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_configure_qemu(self, docker_mock: Mock) -> None:
        """
        Ensure that all possible QEMU files are created as to avoid further complications.
        """
        docker_mock.return_value = docker_mock

        plugin = Plugin(TEST_DISTRO, [])
        plugin.configure_qemu()

        docker_mock.run_container.assert_called_once_with(
            'qus',
            'aptman/qus',
            command=['-s -- -c -p'],
            privileged=True,
            remove=True,
        )

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_delete_qemu(self, docker_mock: Mock) -> None:
        """
        Ensure that all possible QEMU files are removed as expected.
        """
        docker_mock.return_value = docker_mock

        plugin = Plugin(TEST_DISTRO, [])
        plugin.delete_qemu_files()

        docker_mock.run_container.assert_called_once_with(
            'qus',
            'aptman/qus',
            command=['-- -r'],
            privileged=True,
            remove=True,
        )

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_create_builder(self, docker_mock: Mock) -> None:
        """
        Ensure that BuildX builders are created as expected.
        """
        docker_mock.return_value = docker_mock

        plugin = Plugin(TEST_DISTRO, [])
        plugin.create_builder()

        docker_mock.create_builder.assert_called_once_with(TEST_BUILDER_NAME, use=True)

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_remove_builder(self, docker_mock: Mock) -> None:
        """
        Ensure that BuildX builders are removed as expected.
        """
        docker_mock.return_value = docker_mock

        plugin = Plugin(TEST_DISTRO, [])
        plugin.remove_builder()

        docker_mock.remove_builder.assert_called_once_with(TEST_BUILDER_NAME)

    @patch('rigel.plugins.core.buildx.plugin.Plugin.login')
    @patch('rigel.plugins.core.buildx.plugin.Plugin.configure_qemu')
    @patch('rigel.plugins.core.buildx.plugin.Plugin.create_builder')
    def test_setup_mechanism(self, create_builder_mock: Mock, configure_qemu_files: Mock, login_mock: Mock) -> None:
        """
        Ensure that the mechanism to allocate plugin resources works as expected.
        """
        plugin = Plugin(TEST_DISTRO, [
            ('test_target_0', DUMMY_NO_REGISTRY_MODEL.package, self.get_initial_data(DUMMY_NO_REGISTRY_MODEL)),
            ('test_target_1', DUMMY_STANDARD_MODEL.package, self.get_initial_data(DUMMY_STANDARD_MODEL))
        ])
        plugin.setup()

        configure_qemu_files.assert_called_once_with()
        create_builder_mock.assert_called_once_with()

        login_mock.assert_called_once_with(DUMMY_STANDARD_MODEL.package.registries[0])

    @patch('rigel.plugins.core.buildx.plugin.Plugin.logout')
    @patch('rigel.plugins.core.buildx.plugin.Plugin.delete_qemu_files')
    @patch('rigel.plugins.core.buildx.plugin.Plugin.remove_builder')
    def test_stop_mechanism(self, remove_builder_mock: Mock, delete_qemu_files: Mock, logout_mock: Mock) -> None:
        """
        Ensure that the mechanism to release plugin resources works as expected.
        """
        plugin = Plugin(TEST_DISTRO, [
            ('test_target_0', DUMMY_NO_REGISTRY_MODEL.package, self.get_initial_data(DUMMY_NO_REGISTRY_MODEL)),
            ('test_target_1', DUMMY_STANDARD_MODEL.package, self.get_initial_data(DUMMY_STANDARD_MODEL))
        ])
        plugin.stop()

        delete_qemu_files.assert_called_once_with()
        remove_builder_mock.assert_called_once_with()
        logout_mock.assert_called_once_with(DUMMY_STANDARD_MODEL.package.registries[0])

    @patch('rigel.plugins.core.buildx.plugin.DockerClient')
    def test_run_mechanism(self, docker_mock: Mock) -> None:
        """
        Ensure that the plugin works as expected.
        """
        docker_mock.return_value = docker_mock

        plugin = Plugin(TEST_DISTRO, [
            ('test_target_0', DUMMY_NO_REGISTRY_MODEL.package, self.get_initial_data(DUMMY_NO_REGISTRY_MODEL)),
            ('test_target_1', DUMMY_STANDARD_MODEL.package, self.get_initial_data(DUMMY_STANDARD_MODEL)),
            ('test_target_2', DUMMY_ECR_MODEL.package, self.get_initial_data(DUMMY_ECR_MODEL))
        ])
        plugin.run()

        calls = [
            call(DUMMY_NO_REGISTRY_MODEL.package.dir, **{
                "file": f'{DUMMY_NO_REGISTRY_MODEL.package.dir}/Dockerfile',
                "tags": DUMMY_NO_REGISTRY_MODEL.image,
                "load": DUMMY_NO_REGISTRY_MODEL.load,
                "push": DUMMY_NO_REGISTRY_MODEL.push,
                "build_args": DUMMY_NO_REGISTRY_MODEL.buildargs,
            }),
            call('standard_dir', **{
                "file": f'{DUMMY_STANDARD_MODEL.package.dir}/Dockerfile',
                "tags": DUMMY_STANDARD_MODEL.image,
                "load": DUMMY_STANDARD_MODEL.load,
                "push": DUMMY_STANDARD_MODEL.push,
                "build_args": {'TEST': 'STANDARD', 'STANDARD_REGISTRY_ENV':  'test-standard-registry-url'},
            }),
            call('ecr_dir', **{
                "file": f'{DUMMY_ECR_MODEL.package.dir}/Dockerfile',
                "tags": DUMMY_ECR_MODEL.image,
                "load": DUMMY_ECR_MODEL.load,
                "push": DUMMY_ECR_MODEL.push,
                "build_args": DUMMY_ECR_MODEL.buildargs,
                "platforms": DUMMY_ECR_MODEL.platforms
            })
        ]

        docker_mock.build.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()
