import unittest
from rigel.cli.command import CLICommand
from unittest.mock import MagicMock


class DummyCLICommand(CLICommand):
    """ Dummy CLI command for test purposes.
    """
    def __init__(self):
        super().__init__(command='dummy')


class RunJobCommandTesting(unittest.TestCase):
    """
    Test suite for rigel.cli.run.RunJobCommand class.
    """

    def test_add_to_group(self) -> None:
        """
        Ensure the addition of subcommands to the CLI
        works as expected.
        """

        click_group_mock = MagicMock()

        command = DummyCLICommand()
        command.add_to_group(click_group_mock)

        click_group_mock.add_command.assert_called_once_with(
            command.__dict__['_CLICommand__click_group']
        )


if __name__ == '__main__':
    unittest.main()
