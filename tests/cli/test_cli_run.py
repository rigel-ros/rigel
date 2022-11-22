import unittest
from click.testing import CliRunner
from rigel.cli.run import RunJobCommand
from rigel.exceptions import RigelError
from unittest.mock import MagicMock, Mock, patch


class RunJobCommandTesting(unittest.TestCase):
    """
    Test suite for rigel.cli.run.RunJobCommand class.
    """

    __command = RunJobCommand()

    @patch('rigel.cli.run.WorkspaceManager')
    def test_subcommand_job(self, manager_mock: Mock) -> None:
        """
        Ensure that the command 'rigel run job' delegates execution
        flow as expected.
        """
        manager_instance_mock = MagicMock()
        manager_mock.return_value = manager_instance_mock

        test_job = 'test'

        runner = CliRunner()
        runner.invoke(self.__command.job, [test_job])

        manager_mock.assert_called_once_with('./Rigelfile')
        manager_instance_mock.run_job.assert_called_once_with(test_job)

    @patch('rigel.cli.run.WorkspaceManager')
    def test_subcommand_job_exception(self, manager_mock: Mock) -> None:
        """
        Ensure that the command 'rigel run job' handles errors as expected.
        """
        manager_mock.side_effect = RigelError()

        runner = CliRunner()
        result = runner.invoke(self.__command.job, ['test'])
        assert result.exit_code == 1

    @patch('rigel.cli.run.WorkspaceManager')
    def test_subcommand_sequence(self, manager_mock: Mock) -> None:
        """
        Ensure that the command 'rigel run sequence' delegates execution
        flow as expected.
        """
        manager_instance_mock = MagicMock()
        manager_mock.return_value = manager_instance_mock

        test_sequence = 'test'

        runner = CliRunner()
        runner.invoke(self.__command.sequence, [test_sequence])

        manager_mock.assert_called_once_with('./Rigelfile')
        manager_instance_mock.run_sequence.assert_called_once_with(test_sequence)

    @patch('rigel.cli.run.WorkspaceManager')
    def test_subcommand_sequence_exception(self, manager_mock: Mock) -> None:
        """
        Ensure that the command 'rigel run sequence' handles errors as expected.
        """
        manager_mock.side_effect = RigelError()

        runner = CliRunner()
        result = runner.invoke(self.__command.sequence, ['test'])
        assert result.exit_code == 1


if __name__ == '__main__':
    unittest.main()
