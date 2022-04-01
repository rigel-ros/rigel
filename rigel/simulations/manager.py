from .requirement import SimulationRequirement
from rigelcore.clients import ROSBridgeClient
from typing import List


class SimulationRequirementsManager:

    requirements: List[SimulationRequirement]

    def __init__(self) -> None:
        self.requirements = []

    def add_simulation_requirement(self, requirement: SimulationRequirement) -> None:
        """
        Add a simulation requirement.

        :param requirement: The simulation requirement to be added.
        :type requirement: SimulationRequirement
        """
        self.requirements.append(requirement)

    @property
    def requirements_satisfied(self) -> bool:
        """
        Tell whether or not all simulation requirements were satisfied.

        :return: True if all simulation requirements were satisfied. False otherwise.
        :rtype: bool
        """
        if self.requirements:
            return False not in [requirement.satisfied for requirement in self.requirements]
        return False  # when no requirements are specified run simulation until timeout is reached.

    def connect_requirements_to_rosbridge(self, rosbridge_client: ROSBridgeClient) -> None:
        """
        Ensure that all simulation requirements are assessed based
        on the same ROS client.

        :param rosbridge_client: The ROS bridge client.
        :type rosbridge_client: ROSBridgeClient
        """
        for requirement in self.requirements:
            requirement.connect_to_rosbridge(rosbridge_client)

    def __str__(self) -> str:
        message = f"SIMULATION REQUIREMENTS ({'UN' if not self.requirements_satisfied else ''}SATISFIED)"
        for requirement in self.requirements:
            message = message + f'\t{requirement}\n'
        return message
