import unittest
from rigel.simulations.strategy import (
    assess_condition,
    assess_different,
    assess_equal,
    assess_greater,
    assess_greater_than,
    assess_lesser,
    assess_lesser_than
)
from rigel.simulations import AssessmentStrategy, SingleMatchAssessmentStrategy
from unittest.mock import Mock, patch


class AssessmentOperationsTesting(unittest.TestCase):
    """
    Test suite for all isolated functions declared within rigel.simulations.strategy.py
    """

    min_value = 24
    max_value = 42

    def test_access_equal(self) -> None:
        """
        Ensure that the mechanism to test if two values are equal works as expected.
        """
        self.assertTrue(assess_equal(self.min_value, self.min_value))
        self.assertTrue(assess_equal(self.max_value, self.max_value))
        self.assertFalse(assess_equal(self.min_value, self.max_value))
        self.assertFalse(assess_equal(self.max_value, self.min_value))

    def test_access_different(self) -> None:
        """
        Ensure that the mechanism to test if two values are different works as expected.
        """
        self.assertFalse(assess_different(self.min_value, self.min_value))
        self.assertFalse(assess_different(self.max_value, self.max_value))
        self.assertTrue(assess_different(self.min_value, self.max_value))
        self.assertTrue(assess_different(self.max_value, self.min_value))

    def test_assess_lesser(self) -> None:
        """
        Ensure that the mechanism to test if a value is lesser than another value works as expected.
        """
        self.assertFalse(assess_lesser(self.min_value, self.min_value))
        self.assertFalse(assess_lesser(self.max_value, self.max_value))
        self.assertTrue(assess_lesser(self.min_value, self.max_value))
        self.assertFalse(assess_lesser(self.max_value, self.min_value))

    def test_assess_lesser_than(self) -> None:
        """
        Ensure that the mechanism to test if a value is lesser than or equal to another value works as expected.
        """
        self.assertTrue(assess_lesser_than(self.min_value, self.min_value))
        self.assertTrue(assess_lesser_than(self.max_value, self.max_value))
        self.assertTrue(assess_lesser_than(self.min_value, self.max_value))
        self.assertFalse(assess_lesser_than(self.max_value, self.min_value))

    def test_assess_greater(self) -> None:
        """
        Ensure that the mechanism to test if a value is greater than other value works as expected.
        """
        self.assertFalse(assess_greater(self.min_value, self.min_value))
        self.assertFalse(assess_greater(self.max_value, self.max_value))
        self.assertFalse(assess_greater(self.min_value, self.max_value))
        self.assertTrue(assess_greater(self.max_value, self.min_value))

    def test_assess_greater_than(self) -> None:
        """
        Ensure that the mechanism to test if a value is greater than or equal to another value works as expected.
        """
        self.assertTrue(assess_greater_than(self.min_value, self.min_value))
        self.assertTrue(assess_greater_than(self.max_value, self.max_value))
        self.assertFalse(assess_greater_than(self.min_value, self.max_value))
        self.assertTrue(assess_greater_than(self.max_value, self.min_value))

    @patch('rigel.simulations.strategy.assess_equal')
    def test_access_condition_equal(self, assess_mock: Mock) -> None:
        """
        Ensure that the mechanism to assess conditions works as expected for the '=' operator.
        """
        assess_mock.return_value = True  # forcing a wrong value to ensure result is returned as expected
        result = assess_condition(self.min_value, '=', self.max_value)
        assess_mock.assert_called_once_with(self.min_value, self.max_value)
        self.assertTrue(result)

    @patch('rigel.simulations.strategy.assess_different')
    def test_access_condition_different(self, assess_mock: Mock) -> None:
        """
        Ensure that the mechanism to assess conditions works as expected for the '!=' operator.
        """
        assess_mock.return_value = False  # forcing a wrong value to ensure result is returned as expected
        result = assess_condition(self.min_value, '!=', self.max_value)
        assess_mock.assert_called_once_with(self.min_value, self.max_value)
        self.assertFalse(result)

    @patch('rigel.simulations.strategy.assess_lesser')
    def test_access_condition_lesser(self, assess_mock: Mock) -> None:
        """
        Ensure that the mechanism to assess conditions works as expected for the '<' operator.
        """
        assess_mock.return_value = False  # forcing a wrong value to ensure result is returned as expected
        result = assess_condition(self.min_value, '<', self.max_value)
        assess_mock.assert_called_once_with(self.min_value, self.max_value)
        self.assertFalse(result)

    @patch('rigel.simulations.strategy.assess_lesser_than')
    def test_access_condition_lesser_than(self, assess_mock: Mock) -> None:
        """
        Ensure that the mechanism to assess conditions works as expected for the '<=' operator.
        """
        assess_mock.return_value = False  # forcing a wrong value to ensure result is returned as expected
        result = assess_condition(self.min_value, '<=', self.max_value)
        assess_mock.assert_called_once_with(self.min_value, self.max_value)
        self.assertFalse(result)

    @patch('rigel.simulations.strategy.assess_greater')
    def test_access_condition_greater(self, assess_mock: Mock) -> None:
        """
        Ensure that the mechanism to assess conditions works as expected for the '>' operator.
        """
        assess_mock.return_value = True  # forcing a wrong value to ensure result is returned as expected
        result = assess_condition(self.min_value, '>', self.max_value)
        assess_mock.assert_called_once_with(self.min_value, self.max_value)
        self.assertTrue(result)

    @patch('rigel.simulations.strategy.assess_greater_than')
    def test_access_condition_greater_than(self, assess_mock: Mock) -> None:
        """
        Ensure that the mechanism to assess conditions works as expected for the '>=' operator.
        """
        assess_mock.return_value = True  # forcing a wrong value to ensure result is returned as expected
        result = assess_condition(self.min_value, '>=', self.max_value)
        assess_mock.assert_called_once_with(self.min_value, self.max_value)
        self.assertTrue(result)


class AssessmentStrategyTesting(unittest.TestCase):
    """
    Test suite for rigel.simulations.AssessmentStrategy class.
    """

    def test_requirement_default_finished_value(self) -> None:
        """
        Test if by default all strategies are unfinished.
        """
        strategy = AssessmentStrategy()
        self.assertFalse(strategy.finished)

    def test_assess_not_implemented_error(self) -> None:
        """
        Ensure that an instance of NotImplementedError is thrown
        if an assessment mechanism per se is not implement.
        """
        with self.assertRaises(NotImplementedError):
            requirement = AssessmentStrategy()
            requirement.assess('', '', '')


class SingleMatchAssessmentStrategyTesting(unittest.TestCase):
    """
    Test suite for rigel.simulations.SingleMatchAssessmentStrategy class.
    """

    @patch('rigel.simulations.strategy.assess_condition')
    def test_assessment_true(self, assess_mock: Mock) -> None:
        """
        Test if the 'finished' flag is set to True if the assessment condition also returns True.
        """
        test_field = 'test_field'
        test_operator = 'test_operator'
        test_value = 'test_value'

        assess_mock.return_value = True

        strategy = SingleMatchAssessmentStrategy()
        strategy.assess(test_field, test_operator, test_value)

        assess_mock.assert_called_once_with(test_field, test_operator, test_value)
        self.assertTrue(strategy.finished)

    @patch('rigel.simulations.strategy.assess_condition')
    def test_assessment_false(self, assess_mock: Mock) -> None:
        """
        Test if the 'finished' flag remains False if the assessment condition also returns False.
        """
        test_field = 'test_field'
        test_operator = 'test_operator'
        test_value = 'test_value'

        assess_mock.return_value = False

        strategy = SingleMatchAssessmentStrategy()
        strategy.assess(test_field, test_operator, test_value)

        assess_mock.assert_called_once_with(test_field, test_operator, test_value)
        self.assertFalse(strategy.finished)

    @patch('rigel.simulations.strategy.assess_condition')
    def test_assessment_when_finished(self, assess_mock: Mock) -> None:
        """
        Ensure assessment mechanism doesn't work once the 'finished' flag is set to True.
        """
        test_field = 'test_field'
        test_operator = 'test_operator'
        test_value = 'test_value'

        strategy = SingleMatchAssessmentStrategy()
        strategy.finished = True

        strategy.assess(test_field, test_operator, test_value)

        assess_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
