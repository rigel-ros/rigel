from .requirement import SimpleSimulationRequirement
from hpl.parser import property_parser
from hpl.visitor import (
    HplAstVisitor,
    HplBinaryOperator,
    HplFieldAccess,
    HplLiteral,
    HplPattern,
    HplSimpleEvent
)
from typing import Any, Dict, List


class SimulationRequirementsVisitor(HplAstVisitor):
    """
    A class to extract simulation requirements from the nodes of a transformed HPL AST.
    """

    pattern: int
    requirement: Dict[str, Any]
    requirements: List[SimpleSimulationRequirement]

    def __init__(self) -> None:
        """
        Class constructor.
        Initializes internal data structures.
        """
        self.pattern = 0  # invalid pattern
        self.requirement = {}
        self.requirements = []

    def add_requirement(self) -> None:
        """
        Adds a new simulation requirement.
        Assumes all requirement information was already extracted from the HPL AST.
        """
        if self.requirement:  # ensure that a minimum of information has been gathered first.
            requirement = SimpleSimulationRequirement(
                self.pattern,
                self.requirement['topic'],
                self.requirement['msg_type'],
                (
                    self.requirement['field'],
                    self.requirement['operator'],
                    self.requirement['value']
                )
            )
            self.requirements.append(requirement)
            self.requirement = {}

    def visit_hpl_simple_event(self, node: HplSimpleEvent) -> None:
        """
        Extract information from a node of type HplSimpleEvent.
        :param node: The HPL AST node.
        :type node: HplSimpleEvent
        """

        # HplSimpleEvent nodes mark the point where the information about an old requirement
        # ends and information about a new simulation requirement begins.
        # Therefore all previously gathered data must be saved before advancing.
        self.add_requirement()

        self.requirement['topic'] = node.topic.value
        self.requirement['msg_type'] = node.msg_type.value

    def visit_hpl_pattern(self, node: HplPattern) -> None:
        """
        Extract information from a node of type HplPattern.

        :param node: The APL AST node.
        :type node: HplPattern
        """
        self.pattern = node.pattern_type

    def visit_hpl_binary_operator(self, node: HplBinaryOperator) -> None:
        """
        Extract information from a node of type HplBinaryOperator.

        :param node: The APL AST node.
        :type node: HplBinaryOperator
        """
        self.requirement['operator'] = node.operator.value

    def visit_hpl_field_access(self, node: HplFieldAccess) -> None:
        """
        Extract information from a node of type HplFieldAccess.

        :param node: The APL AST node.
        :type node: HplFieldAccess
        """
        self.requirement['field'] = node.field.value

    def visit_hpl_literal(self, node: HplLiteral) -> None:
        """
        Extract information from a node of type HplLiteral.

        :param node: The APL AST node.
        :type node: HplLiteral
        """
        # NOTE: numerical primitive data values and 'bool'
        # have a different access mechanism than 'str'
        for t in [int, float, bool]:
            if isinstance(node.value, t):
                self.requirement['value'] = node.value
                return
        self.requirement['value'] = node.value.value  # for 'str' typed values


class SimulationRequirementsParser:
    """
    A class to parse simulation requirements.
    All simulation requirements must be declared in the HPL language.
    """

    def __init__(self) -> None:
        """
        Class constructor.
        """
        self.parser = property_parser()

    def parse(self, hpl_requirement: str) -> List[SimpleSimulationRequirement]:
        """
        Parse a single simulation requirement.
        All simulation requirements must be expressed in the HPL language.

        :param hpl_requirement: A simulation requirement expressed in the HPL language.
        :type hpl_requirement: str
        :return: The list of declared simulation requirements.
        :rtype: List[SimpleSimulationRequirement]
        """
        visitor = SimulationRequirementsVisitor()

        ast = self.parser.parse(hpl_requirement)
        for node in ast.iterate():
            node.accept(visitor)
        visitor.add_requirement()  # ensures that last parsed simulation requirement is stored.

        return visitor.requirements
