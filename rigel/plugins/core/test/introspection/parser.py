from hpl.parser import property_parser
from hpl.visitor import (
    HplAstVisitor,
    HplEvent,
    HplEventDisjunction,
    HplPattern,
    HplSimpleEvent,
    HplVacuousTruth
)
from typing import Optional
from .callback import CallbackGenerator
from .requirements import (
    AbsenceSimulationRequirementNode,
    DisjointSimulationRequirementNode,
    ExistenceSimulationRequirementNode,
    PreventionSimulationRequirementNode,
    RequirementSimulationRequirementNode,
    ResponseSimulationRequirementNode,
    SimpleSimulationRequirementNode,
    SimulationRequirementNode
)


class SimulationRequirementsVisitor(HplAstVisitor):
    """
    A class to extract simulation requirements from the nodes of a transformed HPL AST.
    """

    requirement: Optional[SimulationRequirementNode]

    def __init__(self) -> None:
        """
        Class constructor.
        Initializes internal data structures.
        """
        self.requirement = None

    def __initialize_disjunction_requirement_event(self, event: HplEventDisjunction) -> SimulationRequirementNode:
        """
        Creates an instance of DisjointSimulationRequirementNode by iterating over an instance of HplEventDisjunction.

        :type event: HplEventDisjunction
        :param event: Placeholder of all information regarding a disjoint simulation requirement node.
        :rtype: SimulationRequirementNode
        :return: A simulation requirement node.
        """
        disjoint_node = DisjointSimulationRequirementNode()

        # Parse "event1"
        child1 = self.__extract_simulation_requirement_node(event.event1)
        disjoint_node.children.append(child1)
        child1.father = disjoint_node

        # Parse "event2"
        child2 = self.__extract_simulation_requirement_node(event.event2)
        disjoint_node.children.append(child2)
        child2.father = disjoint_node

        return disjoint_node

    def __initialize_simple_requirement_node(self, event: HplSimpleEvent) -> SimulationRequirementNode:
        """
        Creates an instance of SimulationRequirementNode by iterating over an instance of HlpSimpleEvent.

        :type event: HplSimpleEvent
        :param event: Placeholder for all information regarding a disjoint simulation requirement node.
        :rtype: SimulationRequirementNode
        :return: A simulation requirement node.
        """
        generator = CallbackGenerator()
        if isinstance(event.predicate, HplVacuousTruth):
            callback = generator.process_vacuous_truth()
        else:
            callback = generator.process_binary_operator(event.predicate.condition)

        simple_node = SimpleSimulationRequirementNode(
            event.topic.value,
            event.msg_type.value,
            callback,
            predicate=str(event.predicate)
        )
        return simple_node

    def __extract_simulation_requirement_node(self, event: HplEvent) -> SimulationRequirementNode:
        """
        Creates an instance of SimulationRequirementNode by iterating over an instance of HplEvent.

        :type event: HplEvent
        :param event: Placeholder for all information regarding a simulation requirement node.
        :rtype: SimulationRequirementNode
        :return: A simulation requirement node.
        """
        if isinstance(event, HplSimpleEvent):
            return self.__initialize_simple_requirement_node(event)
        elif isinstance(event, HplEventDisjunction):
            return self.__initialize_disjunction_requirement_event(event)
        else:
            # TODO: proper error handler
            raise Exception(f'Unknown HplEvent subclass {type(event)}')

    def visit_hpl_pattern(self, node: HplPattern) -> None:
        """
        Extract information from a node of type HplPattern.

        :param node: The HPL AST node.
        :type node: HplPattern
        """
        if node.is_existence:
            self.requirement = ExistenceSimulationRequirementNode(timeout=node.max_time)
        elif node.is_absence:
            self.requirement = AbsenceSimulationRequirementNode(timeout=node.max_time)
        elif node.is_response:
            self.requirement = ResponseSimulationRequirementNode(timeout=node.max_time)
        elif node.is_requirement:
            self.requirement = RequirementSimulationRequirementNode(timeout=node.max_time)
        elif node.is_prevention:
            self.requirement = PreventionSimulationRequirementNode(timeout=node.max_time)

        assert isinstance(self.requirement, SimulationRequirementNode)

        for child in node.children():
            child_node = self.__extract_simulation_requirement_node(child)
            child_node.father = self.requirement
            self.requirement.children.append(child_node)


class SimulationRequirementsParser:
    """
    A class to parse simulation requirements.
    All simulation requirements must be declared in the HPL language.
    """

    def __init__(self) -> None:
        """
        Class constructor.
        """
        self.__parser = property_parser()

    def parse(self, hpl_requirement: str) -> SimulationRequirementNode:
        """
        Parse a single simulation requirement.
        All simulation requirements must be expressed in the HPL language.

        :param hpl_requirement: A simulation requirement expressed in the HPL language.
        :type hpl_requirement: str
        :return: A tree of simulation requirements.
        :rtype: SimulationRequirementsManager
        """
        visitor = SimulationRequirementsVisitor()

        ast = self.__parser.parse(hpl_requirement)

        for node in ast.iterate():
            node.accept(visitor)

        assert isinstance(visitor.requirement, SimulationRequirementNode)
        return visitor.requirement
