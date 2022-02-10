import unittest
from mock import MagicMock, patch
from rigel.docker.builder import ImageBuilder
from rigel.exceptions import DockerBuildError


class ImageBuilderTesting(unittest.TestCase):
    """
    Test suite for rigel.docker.build.ImageBuilder class.
    """

    @patch('rigel.docker.builder.docker.APIClient')
    @patch('rigel.docker.builder.ImageConfigurationFile')
    @patch('rigel.docker.builder.os.environ')
    @patch('rigel.docker.builder.DockerLogPrinter')
    @patch('rigel.docker.builder.MessageLogger')
    def test_docker_with_buildargs(
        self,
        logger_mock,
        printer_mock,
        environ_mock,
        configuration_mock,
        docker_mock) -> None:
        """
        Test if build_args are properly created whenever an SSH key is defined.
        """
        image = 'test_image_with_buildargs'
        key_name = 'test_value'
        key_value = 42

        key_mock = MagicMock()
        key_mock.value = key_name
        configuration_mock.ssh = [key_mock]
        configuration_mock.image = image

        environ_mock.get.return_value = key_value

        docker_client_instance = MagicMock()
        docker_client_instance.build.return_value = [{}]
        docker_mock.return_value = docker_client_instance

        ImageBuilder.build(configuration_mock)

        docker_client_instance.build.assert_called_once_with(
            path='.',
            dockerfile='.rigel_config/Dockerfile',
            tag=image,
            buildargs={key_name: key_value},
            decode=True,
            rm=True,
        )

    @patch('rigel.docker.builder.docker.APIClient')
    @patch('rigel.docker.builder.ImageConfigurationFile')
    @patch('rigel.docker.builder.os.environ')
    @patch('rigel.docker.builder.DockerLogPrinter')
    @patch('rigel.docker.builder.MessageLogger')
    def test_docker_without_buildargs(
        self,
        logger_mock,
        printer_mock,
        environ_mock,
        configuration_mock,
        docker_mock) -> None:
        """
        Test if Docker build works properly.
        """
        image = 'test_image_without_buildags'

        configuration_mock.ssh = {}
        configuration_mock.image = image

        environ_mock.get.return_value = None

        docker_client_instance = MagicMock()
        docker_client_instance.build.return_value = [{}]
        docker_mock.return_value = docker_client_instance

        ImageBuilder.build(configuration_mock)

        docker_client_instance.build.assert_called_once_with(
            path='.',
            dockerfile='.rigel_config/Dockerfile',
            tag=image,
            buildargs={},
            decode=True,
            rm=True,
        )

    @patch('rigel.docker.builder.docker.APIClient')
    @patch('rigel.docker.builder.ImageConfigurationFile')
    @patch('rigel.docker.builder.os.environ')
    @patch('rigel.docker.builder.DockerLogPrinter')
    @patch('rigel.docker.builder.MessageLogger')
    def test_docker_build_error(
        self,
        logger_mock,
        printer_mock,
        environ_mock,
        configuration_mock,
        docker_mock) -> None:
        """
        Test if DockerBuildError is thrown when an error occurs while building a Docker image.
        """
        image = 'test_image_without_buildags'
        error_msg = 'Test error message.'

        configuration_mock.ssh = {}
        configuration_mock.image = image

        environ_mock.get.return_value = None

        docker_client_instance = MagicMock()
        docker_client_instance.build.return_value = [{'error': error_msg}]
        docker_mock.return_value = docker_client_instance

        with self.assertRaises(DockerBuildError):

            ImageBuilder.build(configuration_mock)

            docker_client_instance.build.assert_called_once_with(
                path='.',
                dockerfile='.rigel_config/Dockerfile',
                tag=image,
                buildargs={},
                decode=True,
                rm=True,
            )


if __name__ == '__main__':
    unittest.main()
