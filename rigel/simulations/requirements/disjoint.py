from rigel.simulations.command import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class DisjointSimulationRequirementNode(SimulationRequirementNode):
    """
    A disjoint simulation requirement node consists of a node with at least one child.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

        # Flag that signals when to stop listening for incoming ROS messages.
        self.trigger: bool = False

        # Store the timestamp when a child was last satisfy.
        self.last_message: float = 0.0

    def __str__(self) -> str:
        repr = ''
        for child in self.children:
            repr += f'{str(child)}'
        return repr

    def assess_children_nodes(self) -> bool:
        """
        A disjoint simulation requirement is considered satisfied
        only when at least one of its children simulation requirements is also satisfied.

        :rtype: bool
        :return: True if this simulation requirement is satisfied. False otherwise.
        """
        for child in self.children:

            # NOTE: the following assertion is required so that mypy
            # doesn't throw an error related with multiple inheritance.
            # All 'children' are of type CommandHandler and
            # 'satisfied' is a member of SimulationRequirementNode
            # that inherits from CommandHandler.
            assert isinstance(child, SimulationRequirementNode)

            if child.satisfied:
                return True
        return False

    def handle_trigger(self, command: Command) -> None:
        """
        Handle TRIGGER command sent by father node.

        :param command: Received upstream command.
        :type command: Command
        """
        self.trigger = True
        self.send_downstream_cmd(command)

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by children nodes.
        Whenever a child changes state a disjoint requirement node must check its satisfability.
        """
        if self.assess_children_nodes() != self.satisfied:  # only consider state changes
            self.satisfied = not self.satisfied

            # Inform father node about state change.
            command = CommandBuilder.build_status_change_cmd()
            self.send_upstream_cmd(command)

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
        if command.type in [CommandType.ROSBRIDGE_CONNECT, CommandType.ROSBRIDGE_DISCONNECT]:
            self.send_downstream_cmd(command)
        elif command.type == CommandType.TRIGGER:
            self.handle_trigger(command)
