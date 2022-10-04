from rigel.simulations.command import CommandHandler


class SimulationRequirementNode(CommandHandler):
    """
    Simulation requirements are hierarchical.
    This class serves as a base class for all simulation requirements tree nodes
    and declares the interface that they must comply with.
    """
    # All simulation requirements nodes have a flag
    # that indicates whether or not that requirement was satisfied.
    satisfied: bool = False
