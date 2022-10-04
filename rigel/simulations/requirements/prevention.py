import threading
from math import inf
from rigel.simulations.command import Command, CommandBuilder, CommandType
from .disjoint import DisjointSimulationRequirementNode
from .node import SimulationRequirementNode
from .simple import SimpleSimulationRequirementNode


class PreventionSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures that
    if a ROS message is received that satisfies anterior requirements
    then no other message ROS message is received that satisfies posterior requirements.
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
        An existence simulation requirement is considered satisfied
        only if the posterior requirement is never satisfied after the anterior requirement.

        :rtype: bool
        :return: True if requirement is satisfied. False otherwise.
        """
        anterior = self.children[0]
        posterior = self.children[1]

        # NOTE: the following assertions are required so that mypy
        # doesn't throw an error related with multiple inheritance.
        # All 'children' are of type CommandHandler and
        # 'satisfied' is a member of SimulationRequirementNode
        # that inherits from CommandHandler.
        assert isinstance(anterior, SimulationRequirementNode)
        assert isinstance(posterior, SimulationRequirementNode)

        return anterior.satisfied and not posterior.satisfied

    def handle_timeout(self) -> None:
        """
        Handle timeout events.
        Issue children nodes to stop listening for ROS messages.
        """
        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
        else:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by children nodes.
        Whenever a child changes state a disjoint requirement node must check its satisfability.
        """
        anterior = self.children[0]
        posterior = self.children[1]

        # NOTE: the following assertions are required by mypy.
        # Mypy has no notion of the inner structure of requirements ans must be
        # ensured that children to be of type SimpleSimulationRequirementNode
        # (so that fields 'trigger' and 'last_message' may be accessed).
        assert isinstance(anterior, (DisjointSimulationRequirementNode, SimpleSimulationRequirementNode))
        assert isinstance(posterior, (DisjointSimulationRequirementNode, SimpleSimulationRequirementNode))

        if not posterior.trigger:  # true right after anterior requirement was satisfied
            self.send_child_downstream_cmd(posterior, CommandBuilder.build_trigger_cmd(anterior.last_message))

        # If the posterior requirement is satisfied after the anterior requirement
        # then a point of no return if reached and the assessment can be stopped.
        else:  # anterior.satisfied and posterior.satisfied
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_trigger(self, command: Command) -> None:
        """
        Handle commands of type TRIGGER.
        Forward commad to anterior children.

        :param command: Received command.
        :type command: Command
        """
        # Notify only the anterior requirement node.
        # Posterior node must only start listening for ROS messages after it being satisfied.
        anterior = self.children[0]
        self.send_child_downstream_cmd(anterior, command)

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

        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

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
        elif command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
        elif command.type == CommandType.TRIGGER:
            self.handle_trigger(command)
