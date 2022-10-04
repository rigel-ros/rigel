import roslibpy
from typing import Any, Callable, Dict, List, Tuple


ROS_MESSAGE_TYPE = Dict[str, Any]
ROS_MESSAGE_HANDLER_TYPE = Callable[[ROS_MESSAGE_TYPE], None]


class ROSBridgeClient:
    """
    A wrapper class for the roslibpy.ros.Ros.
    A client for the ROS bridge websocket server.
    """

    handlers: Dict[Tuple[str, str], List[ROS_MESSAGE_HANDLER_TYPE]]
    subscribers: Dict[Tuple[str, str], roslibpy.core.Topic]

    def __init__(self, host: str = 'localhost', port: int = 9090) -> None:
        """
        Class constructor.
        Connects to the ROS bridge websocket server.

        :type host: string
        :param host: The IP address of the ROS bridge websocket server. Defaults to localhost.
        :type port: int
        :param port: The ROS bridge websocket port. Defaults to 9090.
        """
        self.handlers = {}
        self.subscribers = {}

        self.__rosbridge_client = roslibpy.Ros(host=host, port=port)
        self.__rosbridge_client.run()

    def __create_generic_message_handler(self, topic: str, message_type: str) -> ROS_MESSAGE_HANDLER_TYPE:
        """
        Creates a generic message handler function for a specific ROS message type on a specific ROS topic.
        Generic message handlers forward received messages to all registered message handler functions.

        :type topic: string
        :param topic: The ROS topic to subscribe.
        :type message_type: string
        :param message_type: The expected type of incoming ROS messages.

        :rtype: Callable[[Dict[str, Any]], None]
        :return: The message handler function to be executed everytime a ROS message of specified type
        is received on the specified ROS topic.
        """
        def handler_function(message: ROS_MESSAGE_TYPE) -> None:
            key = (topic, message_type)
            if key in self.handlers:
                for message_handler in self.handlers[key]:
                    message_handler(message)

        return handler_function

    def register_message_handler(self, topic: str, message_type: str, handler: ROS_MESSAGE_HANDLER_TYPE) -> None:
        """
        Registers a ROS message handler and starts listening for incoming messages.

        :type topic: string
        :param topic: The ROS topic to subscribe.
        :type message_type: string
        :param message_type: The expected type of incoming ROS messages.
        :type handler: Callable[[Dict[str, Any]], None]
        :param handler: The message handler function to be executed everytime a message is received.
        """
        key = (topic, message_type)

        # Verify if any other handler already exists for the same topic and message type.
        if key in self.handlers:

            if handler not in self.handlers[key]:
                self.handlers[key].append(handler)

        else:  # register provided handler and create new subscriber for the specified topic and message type.

            self.handlers[key] = [handler]

        subscriber = roslibpy.Topic(self.__rosbridge_client, topic, message_type)
        subscriber.subscribe(self.__create_generic_message_handler(topic, message_type))
        self.subscribers[key] = subscriber

    def remove_message_handler(self, topic: str, message_type: str, handler: ROS_MESSAGE_HANDLER_TYPE) -> None:
        """
        Deletes a registered ROS message handler and stops forwarding ROS messages arriving on specified topic.

        :type topic: string
        :param topic: The ROS topic associated with the message handler.
        :type message_type: string
        :param message_type: The type of ROS messages associated with the message handler.
        :type handler: Callable[[Dict[str, Any]], None]
        :param handler: The message handler function to be removed.
        """
        key = (topic, message_type)
        if key in self.handlers:
            if handler in self.handlers[key]:
                self.handlers[key].remove(handler)

                # Verify if any handler is still registered.
                if not self.handlers[key]:

                    del self.handlers[key]
                    self.subscribers[key].unsubscribe()
                    del self.subscribers[key]

    def close(self) -> None:
        """
        Close connection between to the ROS bridge websocket server.
        """
        self.handlers = {}
        for _, subscriber in self.subscribers.items():
            subscriber.unsubscribe()
        self.subscribers = {}
        self.__rosbridge_client.terminate()
