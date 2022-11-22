import python_on_whales
import unittest
from rigel.clients import DockerClient
from rigel.exceptions import DockerAPIError
from unittest.mock import MagicMock, Mock, patch


class DockerClientTesting(unittest.TestCase):
    """
    Test suite for rigel.clients.dockerClient class.
    """

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_get_attribute(self, docker_mock: Mock) -> None:
        """
        Ensure that the Docker client library wrapper works as expected.
        """
        docker_mock.my_test_attribute = 42
        docker_client = DockerClient()
        self.assertEqual(docker_client.my_test_attribute, docker_mock.my_test_attribute)

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_get_attribute_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an AttributeError is thrown in case an attribute does not exist at all.
        """
        test_exception = AttributeError()

        docker_mock.my_test_attribute.side_effect = test_exception
        with self.assertRaises(AttributeError) as context:
            docker_client = DockerClient()
            docker_client.my_test_attribute
        self.assertEqual(context.exception.args, ("No 'DockerClient' object has attribute 'my_test_attribute'",))

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_docker_builder_exists_true(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker builder already exists
        is working as expected.
        """
        test_docker_builder = 'test_docker_builder'

        test_builder = Mock()
        docker_mock.buildx.inspect.return_value = test_builder

        docker_client = DockerClient()
        builder = docker_client.get_builder(test_docker_builder)

        docker_mock.buildx.inspect.assert_called_once_with(test_docker_builder)
        self.assertEqual(builder, test_builder)

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_docker_builder_exists_false(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker builder already exists
        is working as expected.
        """
        test_docker_builder = 'test_docker_builder'

        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.buildx.inspect.side_effect = test_exception

        docker_client = DockerClient()
        builder = docker_client.get_builder(test_docker_builder)

        docker_mock.buildx.inspect.assert_called_once_with(test_docker_builder)
        self.assertIsNone(builder)

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_docker_network_exists_true(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker network already exists
        is working as expected.
        """
        test_docker_network = 'test_docker_network'

        test_network = Mock()
        docker_mock.network.inspect.return_value = test_network

        docker_client = DockerClient()
        network = docker_client.get_network(test_docker_network)

        docker_mock.network.inspect.assert_called_once_with(test_docker_network)
        self.assertEqual(network, test_network)

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_docker_network_exists_false(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker network already exists
        is working as expected.
        """
        test_docker_network = 'test_docker_network'

        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.network.inspect.side_effect = test_exception

        docker_client = DockerClient()
        network = docker_client.get_network(test_docker_network)

        docker_mock.network.inspect.assert_called_once_with(test_docker_network)
        self.assertIsNone(network)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_network')
    def test_create_docker_network_new(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks works as expected.
        """

        test_docker_network_name = 'test_docker_network_name'
        test_docker_network_driver = 'test_docker_network_driver'

        network_mock.return_value = None

        docker_client = DockerClient()
        docker_client.create_network(
            test_docker_network_name,
            test_docker_network_driver
        )

        network_mock.assert_called_once_with(test_docker_network_name)
        docker_mock.network.create.assert_called_once_with(
            test_docker_network_name,
            driver=test_docker_network_driver
        )

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_network')
    def test_create_docker_network_existent(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks first
        verifies if a given Docker network exists before creating it.
        """
        test_docker_network_name = 'test_docker_network_name'
        test_docker_network_driver = 'test_docker_network_driver'

        test_network = Mock()
        network_mock.return_value = test_network

        docker_client = DockerClient()
        network = docker_client.create_network(
            test_docker_network_name,
            test_docker_network_driver
        )

        network_mock.assert_called_once_with(test_docker_network_name)
        docker_mock.network.create.assert_not_called()
        self.assertEqual(network, test_network)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_network')
    def test_docker_create_network_api_error(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while creating a new Docker network using the Docker API.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.network.create.side_effect = test_exception

        network_mock.return_value = None

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.create_network(
                'test_docker_network_name',
                'test_docker_network_driver'
            )
        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_network')
    def test_docker_remove_network_api_error(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while deleting a Docker network using the Docker API.
        """
        test_network_name = 'test_network_name'

        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.network.remove.side_effect = test_exception

        test_network = Mock()
        network_mock.return_value = test_network

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.remove_network(test_network_name)

        network_mock.assert_called_once_with(test_network_name)
        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_network')
    def test_docker_remove_network_unexistent(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a network delete Docker API call is only made if a given network exists.
        """
        test_network_name = 'test_network_name'

        network_mock.return_value = False

        docker_client = DockerClient()
        docker_client.remove_network(test_network_name)

        network_mock.assert_called_once_with(test_network_name)
        docker_mock.network.remove.assert_not_called()

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_network')
    def test_docker_remove_network_existent(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a network delete Docker API call is only made if a given network exists.
        """
        test_network_name = 'test_network_name'

        test_network = Mock()
        network_mock.return_value = test_network

        docker_client = DockerClient()
        docker_client.remove_network(test_network_name)

        network_mock.assert_called_once_with(test_network_name)
        docker_mock.network.remove.assert_called_once_with(test_network)

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_docker_get_container_api_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while retrieving a Docker container information using the Docker API.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.container.exists.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.get_container('test_docker_container')

        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_docker_get_container_exists(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to retrieve Docker containers works as expected.
        """
        test_docker_container_name = 'test_docker_container_name'
        test_container = Mock()

        docker_mock.container.exists.return_value = True
        docker_mock.container.inspect.return_value = test_container

        docker_client = DockerClient()
        container = docker_client.get_container(test_docker_container_name)

        docker_mock.container.exists.assert_called_once_with(test_docker_container_name)
        docker_mock.container.inspect.assert_called_once_with(test_docker_container_name)
        self.assertEqual(container, test_container)

    @patch('rigel.clients.docker.python_on_whales.docker')
    def test_docker_get_container_unexistent(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to retrieve Docker containers works as expected
        if the specified Docker container does not exist.
        """
        test_docker_container_name = 'test_docker_container_name'

        docker_mock.container.exists.return_value = False

        docker_client = DockerClient()
        container = docker_client.get_container(test_docker_container_name)

        docker_mock.container.exists.assert_called_once_with(test_docker_container_name)
        self.assertIsNone(container)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    def test_docker_remove_container_api_error(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a DockerAPIError instance is thrown
        if an error occurs while removing a Docker container using Docker API calls.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_instance_mock.remove.side_effect = test_exception
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.remove_container('test_docker_container_name')
        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    def test_docker_remove_container_exists(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mecanism to delete Docker containers works as expected.
        """
        test_docker_container_name = 'test_docker_container_name'

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_mock.return_value = container_instance_mock

        docker_client = DockerClient()
        docker_client.remove_container(test_docker_container_name)

        container_mock.assert_called_once_with(test_docker_container_name)
        container_instance_mock.remove.assert_called_once_with(force=True, volumes=True)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    def test_docker_remove_container_unexistent(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mecanism to delete Docker containers works as expected
        when the specified Docker container does not exist.
        """
        test_docker_container_name = 'test_docker_container_name'

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        docker_client = DockerClient()
        docker_client.remove_container(test_docker_container_name)

        container_mock.assert_called_once_with(test_docker_container_name)
        container_instance_mock.remove.assert_not_called()

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    def test_docker_run_container_api_error(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a DockerAPIError instance is thrown
        if an error occurs while running a Docker container using Docker API calls.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.container.run.side_effect = test_exception

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.run_container(
                'test_docker_container_name',
                'test_docker_image_name'
            )
        self.assertEqual(context.exception.exception, test_exception)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    def test_docker_run_container_exists(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a Docker container is only run if no other Docker container
        exists with the same name.
        """
        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_mock.return_value = container_instance_mock

        docker_client = DockerClient()
        container = docker_client.run_container(
            'test_docker_container_name',
            'test_docker_image_name'
        )
        self.assertEqual(container, container_instance_mock)

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    def test_docker_run_container_unexistent(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to run Docker containers works as expected.
        """
        test_name = 'test_docker_container_name'
        test_image = 'test_docker_image_name'
        test_kwargs = {'dummy_key': 'dummy_value'}

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        test_container = Mock()
        docker_mock.container.run.return_value = test_container

        docker_client = DockerClient()
        container = docker_client.run_container(
            test_name,
            test_image,
            **test_kwargs
        )

        self.assertEqual(container, test_container)
        docker_mock.container.run.assert_called_once_with(
            test_image,
            name=test_name,
            **test_kwargs
        )

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    def test_wait_container_status_unexistent(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if a Docker container to watch does not exist.
        """
        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError):
            docker_client = DockerClient()
            docker_client.wait_for_container_status('test_container_name', 'test_status')

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    @patch('rigel.clients.docker.time.sleep')
    def test_wait_container_status_timeout(self, sleep_mock: Mock, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if a Docker container to watch does not exist.
        """
        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError):
            docker_client = DockerClient()
            docker_client.wait_for_container_status('test_container_name', 'test_status')

    @patch('rigel.clients.docker.python_on_whales.docker')
    @patch('rigel.clients.docker.DockerClient.get_container')
    @patch('rigel.clients.docker.time.sleep')
    def test_wait_container_status_loop(self, sleep_mock: Mock, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to wait for a given container status value
        to change works as expected.
        """

        test_desired_status = 'test_desired_status'

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_instance_mock.state.status = 'test_invalid_status'
        container_mock.return_value = container_instance_mock

        def update_container_status(time: int) -> None:
            container_instance_mock.state.status = test_desired_status
        sleep_mock.side_effect = update_container_status

        docker_client = DockerClient()
        docker_client.wait_for_container_status('test_container_name', test_desired_status)
        sleep_mock.assert_called_once_with(docker_client.DOCKER_RUN_WAIT_STATUS)


if __name__ == '__main__':
    unittest.main()
