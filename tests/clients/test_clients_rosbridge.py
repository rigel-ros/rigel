import unittest
from rigel.clients import ROSBridgeClient
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch


class ROSBridgeClientTesting(unittest.TestCase):
    """
    Test suite for rigel.clients.ROSBridgeClient class.
    """

    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_client_connection(self, rosbridge_mock: Mock) -> None:
        """
        Ensure that the mechanism to connect to a ROS bridge server works as expected.
        """
        test_host = 'test_host'
        test_port = 12345

        rosbridge_mock.return_value = rosbridge_mock

        ROSBridgeClient(test_host, test_port)

        rosbridge_mock.assert_called_once_with(host=test_host, port=test_port)
        rosbridge_mock.run.assert_called_once()

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_new_handler_registration(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to register message handlers works as expected
        whenever a handler is registered for an unknown topic.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_msg_type = 'test_ros_msg_type'

        def test_message_handler(message: Dict[str, Any]) -> None:
            pass

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        client = ROSBridgeClient('test_host')
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)

        key = (test_ros_topic, test_ros_msg_type)
        self.assertEqual(client.handlers[key], [test_message_handler])
        rostopic_mock.assert_called_once_with(rosbridge_mock, test_ros_topic, test_ros_msg_type)
        rostopic_mock.subscribe.assert_called_once()
        self.assertEqual(client.subscribers[key], rostopic_mock)

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_existing_key_handler_registration(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to register message handlers works as expected
        whenever an handler is registered for an already known topic.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_msg_type = 'test_ros_msg_type'

        def test_message_handler(message: Dict[str, Any]) -> None:
            pass

        def test_another_message_handler(message: Dict[str, Any]) -> None:
            pass

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        client = ROSBridgeClient('test_host')
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_another_message_handler)

        key = (test_ros_topic, test_ros_msg_type)
        self.assertEqual(len(client.handlers[key]), 2)
        self.assertEqual(client.handlers[key][0], test_message_handler)
        self.assertEqual(client.handlers[key][1], test_another_message_handler)

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_repeated_handler_registration(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to register message handlers works as expected
        whenever a same handler is registered multiple times.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_msg_type = 'test_ros_msg_type'

        def test_message_handler(message: Dict[str, Any]) -> None:
            pass

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        client = ROSBridgeClient('test_host')

        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)

        key = (test_ros_topic, test_ros_msg_type)
        self.assertEqual(len(client.handlers[key]), 1)
        self.assertEqual(client.handlers[key][0], test_message_handler)

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_message_forwarding(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to forward incoming ROS message to registered handlers works as expected.
        """
        test_ros_message = {'data': 'Test ROS message.'}
        test_message_handler = MagicMock()

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        client = ROSBridgeClient('test_host')
        client.register_message_handler('test_ros_topic', 'test_ros_msg_type', test_message_handler)

        # Fetch generic handler function associated with subscriber.
        generic_message_handler = rostopic_mock.subscribe.call_args.args[0]
        generic_message_handler(test_ros_message)

        test_message_handler.assert_called_once_with(test_ros_message)

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_message_handler_removal(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to remove registered message handlers works as expected.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_msg_type = 'test_ros_msg_type'

        test_message_handler = MagicMock()
        test_another_message_handler = MagicMock()

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        key = (test_ros_topic, test_ros_msg_type)

        client = ROSBridgeClient('test_host')
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_another_message_handler)

        client.remove_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)

        self.assertEqual(len(client.handlers[key]), 1)
        self.assertEqual(client.handlers[key][0], test_another_message_handler)
        self.assertEqual(len(client.subscribers), 1)

        client.remove_message_handler(test_ros_topic, test_ros_msg_type, test_another_message_handler)

        self.assertEqual(len(client.handlers), 0)
        self.assertEqual(len(client.subscribers), 0)
        rostopic_mock.unsubscribe.assert_called_once()

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_unkown_message_handler_removal(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to remove registered message handlers works as expected
        when removing an unknown message handler.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_msg_type = 'test_ros_msg_type'

        test_message_handler = MagicMock()
        test_another_message_handler = MagicMock()

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        key = (test_ros_topic, test_ros_msg_type)

        client = ROSBridgeClient('test_host')
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)

        client.remove_message_handler(test_ros_topic, test_ros_msg_type, test_another_message_handler)

        self.assertEqual(len(client.handlers), 1)
        self.assertEqual(client.handlers[key][0], test_message_handler)

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_unkown_key_handler_removal(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to remove registered message handlers works as expected
        when removing a message handler for an unknown ROS topic.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_msg_type = 'test_ros_msg_type'

        test_message_handler = MagicMock()

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        key = (test_ros_topic, test_ros_msg_type)

        client = ROSBridgeClient('test_host')
        client.register_message_handler(test_ros_topic, test_ros_msg_type, test_message_handler)

        client.remove_message_handler('unknown_test_ros_topic', 'unknown_test_ros_msg_type', test_message_handler)

        self.assertEqual(len(client.handlers), 1)
        self.assertEqual(client.handlers[key][0], test_message_handler)

    @patch('rigel.clients.rosbridge.roslibpy.Topic')
    @patch('rigel.clients.rosbridge.roslibpy.Ros')
    def test_close(self, rosbridge_mock: Mock, rostopic_mock: Mock) -> None:
        """
        Ensure that the mechanism to remove registered message handlers works as expected
        when removing a message handler for an unknown ROS topic.
        """

        rosbridge_mock.return_value = rosbridge_mock
        rostopic_mock.return_value = rostopic_mock

        client = ROSBridgeClient('test_host')
        client.register_message_handler('test_ros_topic', 'test_ros_msg_type', MagicMock())
        client.close()

        self.assertEqual(len(client.handlers), 0)
        self.assertEqual(len(client.subscribers), 0)
        rostopic_mock.unsubscribe.assert_called_once()
        rosbridge_mock.terminate.assert_called_once()


if __name__ == '__main__':
    unittest.main()
