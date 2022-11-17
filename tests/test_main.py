import unittest
from click.testing import CliRunner
from rigel.main import init
from unittest.mock import Mock, patch


class InitCommandTesting(unittest.TestCase):
    """
    Test suite for rigel.main.init function.
    """

    @patch('rigel.main.os')
    @patch('rigel.main.resource_filename')
    @patch('rigel.main.shutil')
    def test_rigelfile_detection(self, shutil_mock: Mock, resource_mock: Mock, os_mock: Mock) -> None:
        """
        Ensure that the command 'rigel init' detects any existing Rigelfile.
        """
        os_mock.path.exists.return_value = True

        runner = CliRunner()
        runner.invoke(init)

        os_mock.path.exists.assert_called_once_with('./Rigelfile')
        resource_mock.assert_not_called()
        shutil_mock.copyfile.assert_not_called()

    @patch('rigel.main.os')
    @patch('rigel.main.resource_filename')
    @patch('rigel.main.shutil')
    def test_rigelfile_creation(self, shutil_mock: Mock, resource_mock: Mock, os_mock: Mock) -> None:
        """
        Ensure that the command 'rigel init' creates a Rigelfile if none exists.
        """
        os_mock.path.exists.return_value = False

        test_path = 'test_path'
        resource_mock.return_value = test_path

        runner = CliRunner()
        runner.invoke(init)

        os_mock.path.exists.assert_called_once_with('./Rigelfile')
        resource_mock.assert_called_once_with('rigel.main', 'assets/Rigelfile')
        shutil_mock.copyfile.assert_called_once_with(test_path, 'Rigelfile')

    @patch('rigel.main.os')
    @patch('rigel.main.resource_filename')
    @patch('rigel.main.shutil')
    def test_rigelfile_overwrite(self, shutil_mock: Mock, resource_mock: Mock, os_mock: Mock) -> None:
        """
        Ensure that the command 'rigel init' detects and overwrites an existing Rigelfile if desired.s
        """
        os_mock.path.exists.return_value = True

        test_path = 'test_path'
        resource_mock.return_value = test_path

        runner = CliRunner()
        runner.invoke(init, ['--force'])

        os_mock.path.exists.assert_called_once_with('./Rigelfile')
        resource_mock.assert_called_once_with('rigel.main', 'assets/Rigelfile')
        shutil_mock.copyfile.assert_called_once_with(test_path, 'Rigelfile')


if __name__ == '__main__':
    unittest.main()
