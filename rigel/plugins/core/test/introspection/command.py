from __future__ import annotations
from enum import Enum
from rigel.clients import ROSBridgeClient
from typing import Any, Dict, List, Optional


class CommandType(Enum):
    ROSBRIDGE_CONNECT: int = 1
    ROSBRIDGE_DISCONNECT: int = 2
    STATUS_CHANGE: int = 3
    STOP_SIMULATON: int = 4
    TRIGGER: int = 5


class Command:
    """
    A command to be exchanged between simulation requirement nodes.
    """
    def __init__(self, type: CommandType, data: Dict[str, Any]) -> None:
        self.type = type
        self.data = data


class CommandHandler:
    """
    A class for all objects that are able to handle commands and exchange command between themselves.
    """

    # Command handlers form a hierarchical tree.
    # For commands to be exchanged between tree layers
    # each node must have a local notion of the tree structure.
    father: Optional[CommandHandler]
    children: List[CommandHandler]

    # All command handlers must implement a mechanism
    # to handle upstream commands sent by their respective children nodes.
    def handle_upstream_command(self, command: Command) -> None:
        raise NotImplementedError("Please implement this method")

    # All command handlers must implement a mechanism
    # to handle downstream commands sent by their respective father node.
    def handle_downstream_command(self, command: Command) -> None:
        raise NotImplementedError("Please implement this method")

    # All command handlers may send upstream commands
    # to their respective father nodes.
    def send_upstream_cmd(self, command: Command) -> None:
        """
        Send a upstream command to the father node.

        :type command: Command
        :param command: The upstream command to send to the father node.
        """
        if self.father:
            self.father.handle_upstream_command(command)

    # All command handlers may send downstream commands
    # to all of their respective children nodes.
    def send_downstream_cmd(self, command: Command) -> None:
        """
        Send a downstream command to all children nodes.

        :type command: Command
        :param command: The downstream command to send to all children nodes.
        """
        for child in self.children:
            child.handle_downstream_command(command)

    # All command handlers may send downstream commands
    # to a single child node.
    def send_child_downstream_cmd(self, child: CommandHandler, command: Command) -> None:
        """
        Send a downstream command to a single child node.

        :type child: CommandHandler
        :param child: The child node.
        :type command: Command
        :param command: The downstream command to send to the child node.
        """
        child.handle_downstream_command(command)


class CommandBuilder:
    """
    A class to uniformize the creation of Command instances.
    """

    @staticmethod
    def build_rosbridge_connect_cmd(rosbridge_client: ROSBridgeClient) -> Command:
        """
        Build a command that instructs requirement nodes to connect to a ROS bridge client.

        :param rosbridge_client: The ROS bridge client instance.
        :type rosbridge_client: ROSBridgeClient
        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.ROSBRIDGE_CONNECT,
            {'client': rosbridge_client}
        )

    @staticmethod
    def build_rosbridge_disconnect_cmd() -> Command:
        """
        Build a command that instructs requirement nodes to disconnect from a ROS bridge client.

        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.ROSBRIDGE_DISCONNECT,
            {}
        )

    @staticmethod
    def build_status_change_cmd() -> Command:
        """
        Build a command that informs requirement nodes that a children node's state has changed.

        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.STATUS_CHANGE,
            {}
        )

    @staticmethod
    def build_stop_simulation_cmd() -> Command:
        """
        Build a command that informs manager that a simulation requirement has
        unsatisfied and there's no need to continue assessment.

        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.STOP_SIMULATON,
            {}
        )

    @staticmethod
    def build_trigger_cmd(timestamp: float = 0.0) -> Command:
        """
        Build a command that signals a node to stop listening for incoming messages
        once it gets satisfied.

        :param timestamp: The timestamp for oldest received message to be considered satisfied.
        :type timestamp: float, optional
        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.TRIGGER,
            {'timestamp': timestamp}
        )
