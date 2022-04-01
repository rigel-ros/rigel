import unittest
from rigel.simulations import (
    SimpleSimulationRequirement,
    SimulationRequirement
)
from unittest.mock import MagicMock, Mock, patch


class SimulationRequirementTesting(unittest.TestCase):
    """
    Test suite for rigel.simulations.SimulationRequirement class.
    """

    def test_requirement_default_satisfied_value(self) -> None:
        """
        Test if by default all requirements are unsatisfied.
        """
        requirement = SimulationRequirement()
        self.assertFalse(requirement.satisfied)

    def test_connect_not_implemented_error(self) -> None:
        """
        Ensure that an instance of NotImplementedError is thrown
        if requirements don't implement a ROS bridge connection mechanism.
        """
        with self.assertRaises(NotImplementedError):
            requirement = SimulationRequirement()
            requirement.connect_to_rosbridge(Mock())


class SimpleSimulationRequirementTesting(unittest.TestCase):
    """
    Test suite for rigel.simulations.SimpleSimulationRequirement class.
    """

    def test_unknown_pattern_error(self) -> None:
        """
        Test if an instance of Exception is thrown
        whenever an unsupported/unknown pattern is specified.
        """
        test_invalid_pattern = 42
        with self.assertRaises(Exception) as context:
            requirement = SimpleSimulationRequirement(test_invalid_pattern, '', '', ('', '', ''))
            self.assertFalse(requirement.satisfied)
        self.assertEqual(test_invalid_pattern, context.exception.args[1])

    def test_existence_pattern_default_satisfied(self) -> None:
        """
        Test if requirement is initially set to unsatisfied
        whenever using the HplPattern.EXISTENCE pattern.
        """
        requirement = SimpleSimulationRequirement(1, '', '', ('', '', ''))
        self.assertFalse(requirement.satisfied)

    def test_absence_pattern_default_satisfied(self) -> None:
        """
        Test if requirement is initially set to unsatisfied
        whenever using the HplPattern.ABSENCE pattern.
        """
        requirement = SimpleSimulationRequirement(2, '', '', ('', '', ''))
        self.assertTrue(requirement.satisfied)

    def test_connection_rosbridge(self) -> None:
        """
        Test if the ROS bridge server connection mechanism is working as expected.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_message_type = 'test_ros_message_type'

        rosbridge_client_mock = MagicMock()

        requirement = SimpleSimulationRequirement(1, test_ros_topic, test_ros_message_type, ('', '', ''))
        requirement.connect_to_rosbridge(rosbridge_client_mock)

        rosbridge_client_mock.register_message_handler.assert_called_once_with(
            test_ros_topic,
            test_ros_message_type,
            requirement.message_handler
        )

    @patch('rigel.simulations.requirement.SingleMatchAssessmentStrategy')
    def test_handler_assessment(self, strategy_mock: Mock) -> None:
        """
        Ensure that the condition assessment mechanism is working as expected for every ROS message received.
        """
        test_predicate_field = 'test_predicate_field'
        test_predicate_operator = 'test_predicate_operator'
        test_predicate_value = 'test_predicate_value'
        test_predicate = (
            test_predicate_field,
            test_predicate_operator,
            test_predicate_value
        )
        test_ros_message_mock = {'test_predicate_field': test_predicate_field}

        strategy_mock_instance = MagicMock()
        strategy_mock.return_value = strategy_mock_instance
        rosbridge_client_mock = MagicMock()

        requirement = SimpleSimulationRequirement(1, '', '', test_predicate)
        requirement.connect_to_rosbridge(rosbridge_client_mock)
        requirement.message_handler(test_ros_message_mock)

        strategy_mock_instance.assess.assert_called_once_with(
            test_predicate_field,
            test_predicate_operator,
            test_predicate_value
        )

    @patch('rigel.simulations.requirement.SingleMatchAssessmentStrategy')
    def test_remove_handler_mechanism(self, strategy_mock: Mock) -> None:
        """
        Ensure that the mechanism to stop condition assessment works as expected.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_message_type = 'test_ros_message_type'
        test_predicate_field = 'test_predicate_field'
        test_predicate_operator = 'test_predicate_operator'
        test_predicate_value = 'test_predicate_value'
        test_predicate = (
            test_predicate_field,
            test_predicate_operator,
            test_predicate_value
        )
        test_ros_message_mock = {'test_predicate_field': test_predicate_field}

        strategy_mock_instance = MagicMock()
        strategy_mock_instance.finished = True
        strategy_mock.return_value = strategy_mock_instance

        rosbridge_client_mock = MagicMock()

        requirement = SimpleSimulationRequirement(1, test_ros_topic, test_ros_message_type, test_predicate)
        initial_satisfied_value = requirement.satisfied

        requirement.connect_to_rosbridge(rosbridge_client_mock)
        requirement.message_handler(test_ros_message_mock)
        final_satisfied_value = requirement.satisfied

        rosbridge_client_mock.remove_message_handler.assert_called_once_with(
            test_ros_topic,
            test_ros_message_type,
            requirement.message_handler
        )
        self.assertTrue(initial_satisfied_value != final_satisfied_value)

    @patch('rigel.simulations.requirement.SingleMatchAssessmentStrategy')
    def test_loop_mechanism(self, strategy_mock: Mock) -> None:
        """
        Ensure that the mechanism to stop condition assessment works as expected.
        """
        test_ros_topic = 'test_ros_topic'
        test_ros_message_type = 'test_ros_message_type'
        test_predicate_field = 'test_predicate_field'
        test_predicate_operator = 'test_predicate_operator'
        test_predicate_value = 'test_predicate_value'
        test_predicate = (
            test_predicate_field,
            test_predicate_operator,
            test_predicate_value
        )
        test_ros_message_mock = {'test_predicate_field': test_predicate_field}

        strategy_mock_instance = MagicMock()
        strategy_mock_instance.finished = False
        strategy_mock.return_value = strategy_mock_instance

        rosbridge_client_mock = MagicMock()

        requirement = SimpleSimulationRequirement(1, test_ros_topic, test_ros_message_type, test_predicate)
        initial_satisfied_value = requirement.satisfied

        requirement.connect_to_rosbridge(rosbridge_client_mock)
        requirement.message_handler(test_ros_message_mock)
        final_satisfied_value = requirement.satisfied

        rosbridge_client_mock.remove_message_handler.assert_not_called()
        self.assertTrue(initial_satisfied_value == final_satisfied_value)


if __name__ == '__main__':
    unittest.main()
