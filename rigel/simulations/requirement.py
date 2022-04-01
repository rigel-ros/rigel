from .strategy import SingleMatchAssessmentStrategy
from rigelcore.clients import ROSBridgeClient
from typing import Any, Dict, Tuple


ROS_MESSAGE_TYPE = Dict[str, Any]
PREDICATE_TYPE = Tuple[str, str, str]


class SimulationRequirement:
    """
    The base class for all simulation requirements.
    """

    # All simulation requirements share a common attribute
    # that indicates whether or not that requirement was satisfied or not.
    satisfied: bool = False

    # All simulation requirements must have a common interface
    # regarding connecting to a ROS bridge client.
    def connect_to_rosbridge(self, rosbridge_client: ROSBridgeClient) -> None:
        raise NotImplementedError("No mechanism implemented to connect to ROS bridge client.")


class SimpleSimulationRequirement(SimulationRequirement):

    def __init__(
        self,
        pattern: int,
        ros_topic: str,
        ros_message_type: str,
        predicate: PREDICATE_TYPE
    ) -> None:
        """
        Class constructor.
        Selects simulation assessment strategy.

        :param pattern: The pattern to follow.
        :type pattern: int
        :param ros_topic: The ROS topic to subscribe.
        :type ros_topic: str
        :param ros_message_type: The type of expected ROS message.
        :type ros_message_type: PREDICATE_TYPE
        :param predicate: The predicate that must be fulfilled by this predicate.
        :type predicate: Tuple[str, str, str]
        """
        self.ros_topic = ros_topic
        self.ros_message_type = ros_message_type
        self.predicate = predicate

        self.strategy = SingleMatchAssessmentStrategy()
        if pattern == 1:    # HplPattern.EXISTENCE
            self.satisfied = False
        elif pattern == 2:  # HplPattern.ABSENCE
            self.satisfied = True
        else:
            raise Exception("No assessment strategy found for specified pattern", pattern)

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

    def message_handler(self, message: ROS_MESSAGE_TYPE) -> None:
        """
        ROS message handler.
        Applied predicate condition to all messages in order to assess
        simulation requirement.

        :param message: The received ROS message.
        :type message: ROS_MESSAGE_TYPE
        """
        # Retrieve ROS message field.
        # TODO: support nested fields.
        field, operator, value = self.predicate
        msg_field = message[field]

        self.strategy.assess(msg_field, operator, value)

        # Stop listening for messages once the
        # assessment strategy finished executing.
        if self.strategy.finished:
            self.__rosbridge_client.remove_message_handler(
                self.ros_topic,
                self.ros_message_type,
                self.message_handler
            )
            self.satisfied = not self.satisfied

    def __str__(self) -> str:
        field, operator, value = self.predicate
        return "{} [{}] : {} {} {} ({}SATISFIED)".format(
            self.ros_topic,
            self.ros_message_type,
            field,
            operator,
            value,
            'UN' if not self.satisfied else ''
        )
