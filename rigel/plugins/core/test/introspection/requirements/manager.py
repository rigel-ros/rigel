import threading
from .node import SimulationRequirementNode
from rigel.clients import ROSBridgeClient
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from typing import List


class SimulationRequirementsManager(SimulationRequirementNode):
    """
    A simulation requirements manager is responsible for
    controling all different node trees associated with a given simulation.
    """

    def __init__(self, max_timeout: float, min_timeout: float = 0.0) -> None:
        self.children = []
        self.father = None
        self.finished = False

        self.__introspection_started = False

        self.__start_timer = threading.Timer(min_timeout, self.handle_start_timeout)
        self.__stop_timer = threading.Timer(max_timeout, self.handle_stop_timeout)

    def add_child(self, child: SimulationRequirementNode) -> None:
        child.father = self
        self.children.append(child)

    def add_children(self, children: List[SimulationRequirementNode]) -> None:
        for child in children:
            self.add_child(child)

    def __str__(self) -> str:
        if self.children:
            repr = ''
            for child in self.children:
                repr += f'{str(child)}\n'
            return repr
        else:
            return 'No simulation requirements were provided.'

    def connect_to_rosbridge(self, rosbridge_client: ROSBridgeClient) -> None:
        """
        Issues children nodes to start listening for incoming ROS messages.

        :param rosbridge_client: The ROS bridge client.
        :type rosbridge_client: ROSBridgeClient
        """
        # self.send_downstream_cmd(CommandBuilder.build_trigger_cmd())
        self.send_downstream_cmd(CommandBuilder.build_rosbridge_connect_cmd(rosbridge_client))

        self.__start_timer.start()
        self.__stop_timer.start()

    def disconnect_from_rosbridge(self) -> None:
        """
        Issue children nodes to stop listening for incoming ROS messages.
        """
        command = CommandBuilder.build_rosbridge_disconnect_cmd()
        self.send_downstream_cmd(command)

    def stop_timers(self) -> None:
        self.__start_timer.cancel()
        self.__stop_timer.cancel()

    def stop_simulation(self) -> None:
        """
        Stop simulation.
        """
        self.disconnect_from_rosbridge()
        self.finished = True

    def handle_start_timeout(self) -> None:
        """
        Allow simulation to be assessed.
        """
        # Ensure that manager detects if all children requirements are
        # already satisfied whenever the simulation starts.
        # For this emulate reception of a STATUS_CHANGE command.

        self.__introspection_started = True
        self.send_downstream_cmd(CommandBuilder.build_trigger_cmd())
        self.handle_children_status_change()

    def handle_stop_timeout(self) -> None:
        self.stop_simulation()

    def assess_children_nodes(self) -> bool:
        """
        Tell whether or not all simulation requirements were satisfied.

        :return: True if all simulation requirements were satisfied. False otherwise.
        :rtype: bool
        """
        # if self.children:
        if self.children and self.__introspection_started:
            for child in self.children:

                # NOTE: the following assertion is required so that mypy
                # doesn't throw an error related with multiple inheritance.
                # All 'children' are of type CommandHandler and
                # 'satisfied' is a member of SimulationRequirementNode
                # that inherits from CommandHandler.
                assert isinstance(child, SimulationRequirementNode)
                if not child.satisfied:
                    return False

            return True

            # return False not in [child.satisfied for child in self.children]
        return False  # when no requirements are specified run simulation until timeout is reached.

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by children nodes.
        Whenever a child changes state a requirement node must check its satisfability.
        """
        if self.assess_children_nodes() != self.satisfied:  # only consider state changes

            self.satisfied = not self.satisfied
            # Stop simulation once all requirements are satisfied.
            if self.satisfied:
                self.stop_timers()
                self.stop_simulation()

    def handle_stop_simulation(self) -> None:
        """
        Handle STOP_SIMULATON commands sent by children nodes.
        Stops simulation and signals its ending.
        """
        self.stop_timers()
        self.stop_simulation()

    def handle_upstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming upstream commands to their proper handler.

        :param command: Received upstream command.
        :type command: Command
        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()
        elif command.type == CommandType.STOP_SIMULATON:
            self.handle_stop_simulation()
