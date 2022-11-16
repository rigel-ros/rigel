import threading
from math import inf
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from .node import SimulationRequirementNode


class RequirementSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that if a ROS message is received that satisfies anterior requirements
    then all posterior requirements were already previously satisfied.
    """

    def __init__(self, timeout: float = inf) -> None:
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

    def __str__(self) -> str:
        repr = ''
        for child in self.children:
            repr += f'{str(child)}'
        return repr

    def assess_children_nodes(self) -> bool:
        """
        A response simulation requirement consists is considered satisfied
        in any of the following situations:
        - both anterior and posterior requirements are satisfied
        """
        posterior = self.children[0]
        anterior = self.children[1]

        # NOTE: the following assertions are required so that mypy
        # doesn't throw an error related with multiple inheritance.
        # All 'children' are of type CommandHandler and
        # 'satisfied' is a member of SimulationRequirementNode
        # that inherits from CommandHandler.
        assert isinstance(anterior, SimulationRequirementNode)
        assert isinstance(posterior, SimulationRequirementNode)

        if anterior.satisfied and not posterior.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())
        return posterior.satisfied and anterior.satisfied

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by children nodes.
        Whenever a child changes state a disjoint requirement node must check its satisfability.
        """
        if self.assess_children_nodes():  # only consider state changes
            self.satisfied = True

            self.__timer.cancel()
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

    def handle_timeout(self) -> None:
        """
        Handle timeout events.
        Issue children nodes to stop listening for ROS messages.
        """
        if not self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Handle commands of type ROSBRIDGE_CONNECT.
        Forward command to all children nodes and initialize timer thread.

        :param command: Received command.
        :type command: Command
        """
        self.send_downstream_cmd(command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.timeout != inf:  # start timer in case a time limit was specified
            self.__timer.start()

    def handle_rosbridge_disconnection_commands(self, command: Command) -> None:
        """
        Handle commands of type ROSBRIDGE_DISCONNECT.
        Forwars command to all children nodes and stop timer threads.

        :param command: Received command.
        :type command: Command
        """
        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'

        self.send_downstream_cmd(command)

    def handle_upstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming upstream commands to their proper handler.

        :param command: Received upstream command.
        :type command: Command
        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming downstream commands to their proper handler.

        :param command: Received dowstream command.
        :type command: Command
        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.handle_rosbridge_connection_commands(command)
        if command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
        elif command.type == CommandType.TRIGGER:
            self.send_downstream_cmd(command)
