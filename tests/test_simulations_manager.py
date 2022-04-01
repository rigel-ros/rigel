import unittest
from rigel.simulations import SimulationRequirementsManager
from unittest.mock import MagicMock


class SimulationRequirementsManagerTesting(unittest.TestCase):
    """
    Test suite for rigel.simulations.SimulationRequirementsManager class.
    """

    def test_add_simulation_requirement(self) -> None:
        """
        Test if the mechanism to add simulation requirements works as expected.
        """
        requirement_instance_mock = MagicMock()

        requirements_manager = SimulationRequirementsManager()
        self.assertEqual(len(requirements_manager.requirements), 0)

        requirements_manager.add_simulation_requirement(requirement_instance_mock)
        self.assertEqual(len(requirements_manager.requirements), 1)
        self.assertEqual(requirements_manager.requirements[0], requirement_instance_mock)

    def test_satisfied_no_requirements(self) -> None:
        """
        Ensure that scenarios with no simulation requirements always lead to a 'unsatisfied' status.
        """
        requirements_manager = SimulationRequirementsManager()
        self.assertEqual(len(requirements_manager.requirements), 0)
        self.assertFalse(requirements_manager.requirements_satisfied)

    def test_satisfied_with_unsatisfied_requirements(self) -> None:
        """
        Ensure that a 'satisfied' status is only reached when all requirements were satisfied.
        """
        unsatisfied_requirement_instance_mock = MagicMock()
        unsatisfied_requirement_instance_mock.satisfied = False

        another_unsatisfied_requirement_instance_mock = MagicMock()
        another_unsatisfied_requirement_instance_mock.satisfied = False

        requirements_manager = SimulationRequirementsManager()
        requirements_manager.add_simulation_requirement(unsatisfied_requirement_instance_mock)
        requirements_manager.add_simulation_requirement(another_unsatisfied_requirement_instance_mock)

        self.assertEqual(len(requirements_manager.requirements), 2)
        self.assertFalse(requirements_manager.requirements_satisfied)

    def test_satisfied_with_mixed_requirements(self) -> None:
        """
        Ensure that a 'satisfied' status is only reached when all requirements were satisfied.
        """
        unsatisfied_requirement_instance_mock = MagicMock()
        unsatisfied_requirement_instance_mock.satisfied = False

        satisfied_requirement_instance_mock = MagicMock()
        satisfied_requirement_instance_mock.satisfied = True

        requirements_manager = SimulationRequirementsManager()
        requirements_manager.add_simulation_requirement(unsatisfied_requirement_instance_mock)
        requirements_manager.add_simulation_requirement(satisfied_requirement_instance_mock)

        self.assertEqual(len(requirements_manager.requirements), 2)
        self.assertFalse(requirements_manager.requirements_satisfied)

    def test_satisfied_with_satisfied_requirements(self) -> None:
        """
        Ensure that a 'satisfied' status is only reached when all requirements were satisfied.
        """
        satisfied_requirement_instance_mock = MagicMock()
        satisfied_requirement_instance_mock.satisfied = True

        another_satisfied_requirement_instance_mock = MagicMock()
        another_satisfied_requirement_instance_mock.satisfied = True

        requirements_manager = SimulationRequirementsManager()
        requirements_manager.add_simulation_requirement(satisfied_requirement_instance_mock)
        requirements_manager.add_simulation_requirement(another_satisfied_requirement_instance_mock)

        self.assertEqual(len(requirements_manager.requirements), 2)
        self.assertTrue(requirements_manager.requirements_satisfied)

    def test_chained_rosbridge_connection(self) -> None:
        """
        Test if the mechanism to connect all requirements to a same ROS bridge works as expected.
        """
        rosbridge_client_mock = MagicMock()
        requirement_instance_mock = MagicMock()

        requirements_manager = SimulationRequirementsManager()
        requirements_manager.add_simulation_requirement(requirement_instance_mock)
        requirements_manager.connect_requirements_to_rosbridge(rosbridge_client_mock)

        requirement_instance_mock.connect_to_rosbridge.assert_called_once_with(rosbridge_client_mock)


if __name__ == '__main__':
    unittest.main()
