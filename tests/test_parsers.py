import unittest
from dataclasses import dataclass
from mock import patch
from pkg_resources import resource_filename
from rigel.exceptions import (
    IncompleteRigelfileError,
    MissingRequiredFieldError,
    UnknownFieldError
)
from rigel.files import EnvironmentVariable, SSHKey, YAMLDataLoader
from rigel.parsers.injector import YAMLInjector
from rigel.parsers.rigelfile import RigelfileParser


@dataclass
class TestDataclass:
    number: int
    flag: bool


class YAMLInjectorTesting(unittest.TestCase):
    """
    Test suite for rigel.parsers.injector.YAMLInjector class.
    """

    def test_injecting_unknown_field(self) -> None:
        """
        Test if MissingRequiredFieldError is thrown is a required field is not provided.
        """
        with self.assertRaises(MissingRequiredFieldError):
            YAMLInjector.inject(TestDataclass, {})

    def test_injecting_missing_field(self) -> None:
        """
        Test if UnknownFieldError is thrown if a required field is not provided.
        """
        with self.assertRaises(UnknownFieldError):
            YAMLInjector.inject(TestDataclass, {
                'number': 1,
                'flag': True,
                'sentence': "Field 'sentence' is unknown."
            })

    @patch.object(TestDataclass, '__init__')
    def test_injected_data(self, mock_dataclass) -> None:
        """
        Test if the provided data is properly forwarded to the dataclass constructor.
        """
        data = {'number': 1, 'flag': True}
        YAMLInjector.inject(TestDataclass, data)
        mock_dataclass.assert_called_once_with(**data)


class ParserTesting(unittest.TestCase):
    """
    Test suite for rigel.parsers.riglefile.RigelfileParser class.
    """

    def test_missing_build_block(self) -> None:
        """
        Test if IncompleteRigelfileError is thrown if Rigelfile misses 'build' block.
        """
        with self.assertRaises(IncompleteRigelfileError):
            RigelfileParser({})

    @patch.object(EnvironmentVariable, '__init__')
    def test_env_variables_ignored(self, mock_dataclass) -> None:
        """
        Test if no custom environment variable value is stored when field 'env' is left undeclared.
        """
        yaml_file = resource_filename(__name__, 'assets/build_basic')
        yaml_data = YAMLDataLoader.load_data(yaml_file)
        RigelfileParser(yaml_data)

        self.assertFalse(mock_dataclass.called)

    @patch.object(EnvironmentVariable, '__init__')
    def test_env_variables_creation(self, mock_dataclass) -> None:
        """
        Test if custom environment variables' values are properly stored.
        """
        yaml_file = resource_filename(__name__, 'assets/build_complete')
        yaml_data = YAMLDataLoader.load_data(yaml_file)
        RigelfileParser(yaml_data)

        self.assertEqual(len(yaml_data['build']['env']), mock_dataclass.call_count)
        for env in yaml_data['build']['env']:
            name, value = env.strip().split('=')
            mock_dataclass.called_once_with(**{'name': name, 'value': value})

    @patch.object(SSHKey, '__init__')
    def test_ssh_keys_ignored(self, mock_dataclass) -> None:
        """
        Test if no SSH information is stored when field 'ssh' is left undeclared.
        """
        yaml_file = resource_filename(__name__, 'assets/build_basic')
        yaml_data = YAMLDataLoader.load_data(yaml_file)
        RigelfileParser(yaml_data)

        self.assertFalse(mock_dataclass.called)

    @patch.object(SSHKey, '__init__')
    def test_ssh_keys_creation(self, mock_dataclass) -> None:
        """
        Test if custom SSH information is properly stored.
        """
        yaml_file = resource_filename(__name__, 'assets/build_complete')
        yaml_data = YAMLDataLoader.load_data(yaml_file)
        RigelfileParser(yaml_data)

        self.assertEqual(len(yaml_data['build']['ssh']), mock_dataclass.call_count)
        for key in yaml_data['build']['ssh']:
            mock_dataclass.called_once_with(**key)


if __name__ == '__main__':
    unittest.main()
