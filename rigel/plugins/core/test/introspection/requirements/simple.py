import time
from rigel.clients import ROSBridgeClient
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from typing import Any, Callable, Dict

from .disjoint import DisjointSimulationRequirementNode
from .node import SimulationRequirementNode

ROS_MESSAGE_TYPE = Dict[str, Any]


class SimpleSimulationRequirementNode(SimulationRequirementNode):
    """
    A simple simulation requirement node consists of a node without children.
    Simple simulation requirements interface with ROS bridge clients and hande incoming ROS messages.
    """

    def __init__(
            self,
            ros_topic: str,
            ros_message_type: str,
            ros_message_callback: Callable,
            predicate: str
            ) -> None:
        """
        Class constructor.
        Selects simulation assessment strategy.

        :param ros_topic: The ROS topic to subscribe.
        :type ros_topic: str
        :param ros_message_type: The type of expected ROS message.
        :type ros_message_type: str
        """
        self.children = []
        self.father = None

        self.ros_topic = ros_topic
        self.ros_message_type = ros_message_type
        self.ros_message_callback = ros_message_callback
        self.predicate = predicate

        # Store the timestamp when the last message that satisfy this requirement was received.
        self.last_message: float = 0.0

        # Flag that signals when to stop listening for incoming ROS messages.
        self.trigger: bool = False

    def __str__(self) -> str:
        # TODO: use logger to make a more readable output.
        satisfied_msg = str(self.last_message) if self.last_message else "no ROS message received"
        if self.satisfied:
            return f'\n[{self.ros_topic}]\t- SATISFIED\t({satisfied_msg}): {self.predicate}'
        else:
            return f'\n[{self.ros_topic}]\t- UNSATISFIED\t({satisfied_msg}): {self.predicate}'

    def handle_upstream_command(self, command: Command) -> None:
        pass  # NOTE: nodes of this type don't have children and therefore will never receive upstream commands.

    def handle_downstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming downstream commands to their proper handler.

        :param command: Received downstream command.
        :type command: Command
        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.connect_to_rosbridge(command.data['client'])
        elif command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.disconnect_from_rosbridge()
        elif command.type == CommandType.TRIGGER:
            self.handle_trigger(command.data['timestamp'])

    def connect_to_rosbridge(self, rosbridge_client: ROSBridgeClient) -> None:
        """
        Register ROS message handler and start listening for incoming ROS messages.

        :param rosbridge_client: The ROS bridge client.
        :type rosbridge_client: ROSBridgeClient
        """
        self.__rosbridge_client = rosbridge_client
        self.__rosbridge_client.register_message_handler(
            self.ros_topic,
            self.ros_message_type,
            self.message_handler
        )

    def disconnect_from_rosbridge(self) -> None:
        """
        Unregister ROS message handler and stop listening for incoming ROS messages.
        """
        self.__rosbridge_client.remove_message_handler(
            self.ros_topic,
            self.ros_message_type,
            self.message_handler
        )

    def handle_trigger(self, timestamp: float) -> None:
        """
        :param timestamp: Maximum timestamp for last message received.
        :type timestamp: float
        """
        self.trigger = True
        if self.last_message > timestamp:
            self.disconnect_from_rosbridge()
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

    def message_handler(self, message: ROS_MESSAGE_TYPE) -> None:
        """
        ROS message handler.
        Applied predicate condition to all messages in order to assess
        simulation requirement.

        :param message: The received ROS message.
        :type message: ROS_MESSAGE_TYPE
        """
        if self.ros_message_callback(message):

            self.satisfied = True
            self.last_message = time.time()

            if self.trigger:

                if isinstance(self.father, DisjointSimulationRequirementNode):
                    self.father.last_message = self.last_message

                self.disconnect_from_rosbridge()
                self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())
