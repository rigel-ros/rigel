from typing import Any


def assess_equal(field: Any, value: Any) -> bool:
    """
    Verify if a given ROS message field equals a certain reference value.

    :param field: The ROS message field.
    :type field: Any
    :param value: The reference value.
    :type value: Any
    :return: True if the ROS message field and the reference value are equal.
    False otherwise.
    :rtype: bool
    """
    return bool(field == value)


def assess_different(field: Any, value: Any) -> bool:
    """
    Verify if a given ROS message field is different from a certain reference value.

    :param field: The ROS message field.
    :type field: Any
    :param value: The reference value.
    :type value: Any
    :return: True if the ROS message field is different from the reference value.
    False otherwise.
    :rtype: bool
    """
    return bool(field != value)


def assess_lesser(field: Any, value: Any) -> bool:
    """
    Verify if a given ROS message field is lesser than a certain reference value.

    :param field: The ROS message field.
    :type field: Any
    :param value: The reference value.
    :type value: Any
    :return: True if the ROS message field is lesser than the reference value.
    False otherwise.
    :rtype: bool
    """
    return bool(field < value)


def assess_lesser_than(field: Any, value: Any) -> bool:
    """
    Verify if a given ROS message field is lesser than or equal to a certain reference value.

    :param field: The ROS message field.
    :type field: Any
    :param value: The reference value.
    :type value: Any
    :return: True if the ROS message field is lesser than or equal to the reference value.
    False otherwise.
    :rtype: bool
    """
    return bool(field <= value)


def assess_greater(field: Any, value: Any) -> bool:
    """
    Verify if a given ROS message field is greater than a certain reference value.

    :param field: The ROS message field.
    :type field: Any
    :param value: The reference value.
    :type value: Any
    :return: True if the ROS message field is greater than the reference value.
    False otherwise.
    :rtype: bool
    """
    return bool(field > value)


def assess_greater_than(field: Any, value: Any) -> bool:
    """
    Verify if a given ROS message field is greater than or equal to a certain reference value.

    :param field: The ROS message field.
    :type field: Any
    :param value: The reference value.
    :type value: Any
    :return: True if the ROS message field is greater than or equal to the reference value.
    False otherwise.
    :rtype: bool
    """
    return bool(field >= value)


def assess_condition(field: Any, operator: Any, value: Any) -> bool:
    """
    Compare the value of a given ROS message field with a certain reference value.

    :param field: The ROS message field.
    :type field: Any
    :param operator: The comparison to make.
    :type operator: str
    :param value: The reference value.
    :type value: Any
    :return: The result of the comparison between the given ROS message field and the
    provided reference value.
    :rtype: bool
    """
    if operator == '=':
        return assess_equal(field, value)
    elif operator == '!=':
        return assess_different(field, value)
    elif operator == '<':
        return assess_lesser(field, value)
    elif operator == '<=':
        return assess_lesser_than(field, value)
    elif operator == '>':
        return assess_greater(field, value)
    elif operator == '>=':
        return assess_greater_than(field, value)
    else:
        raise Exception(f'No strategy for operator "{operator}".')


class AssessmentStrategy:
    """
    Base class for all assessment strategies.

    :cvar finished: Flag that indicates when to stop assessing incoming ROS messages.
    :type field: Any
    """

    finished = False

    def assess(self, field: Any, operator: str, value: Any) -> None:
        raise NotImplementedError("Invalid simulation requirements assessment strategy.")


class SingleMatchAssessmentStrategy(AssessmentStrategy):
    """
    A requirement assessment strategy that consists in finding
    a single ROS message that satisfies a given condition.
    """

    def assess(self, field: Any, operator: str, value: Any) -> None:
        """
        Assess if a ROS message satisfies a given condition.
        Once a message is found to do that, no more messages are assessed.

        :param field: The ROS message field.
        :type field: Any
        :param operator: The comparison to make and that must be satisfied.
        :type operator: str
        :param value: The reference value.
        :type value: Any
        """
        if not self.finished:
            if assess_condition(field, operator, value):
                self.finished = True
