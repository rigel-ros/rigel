import copy
import unittest
from pydantic import BaseModel
from rigel.exceptions import (
    IncompleteRigelfileError,
    MissingRequiredFieldError,
    PluginNotFoundError,
    UndeclaredGlobalVariable
)
from rigel.files import EnvironmentVariable, SSHKey
from rigel.parsers.decoder import RigelfileDecoder
from rigel.parsers.injector import YAMLInjector
from rigel.parsers.rigelfile import RigelfileParser
from typing import Any, Dict
from unittest.mock import Mock, patch


class TestDataclass(BaseModel):
    """
    A simple class that works as a fake Rigelfile for testing.
    """
    number: int
    flag: bool


class RigelfileDecoderTesting(unittest.TestCase):
    """
    Test suite for rigel.parsers.decoder.RigelfileDecoder class.
    """

    @patch('rigel.parsers.decoder.copy.deepcopy')
    def test_data_deep_copy(self, copy_mock: Mock) -> None:
        """
        Test if original YAML data is preserved before the decoding process.
        """
        test_data = {'test_key': 'test_value'}

        copy_mock.return_value = test_data
        RigelfileDecoder().decode(test_data)
        copy_mock.assert_called_once_with(test_data)

    def test_vars_field_removal(self) -> None:
        """
        Test if the field 'vars' is removed, if declared, before the decoding process.
        """
        test_data_without = {'test_key': 'test_value'}
        test_data_with = {'test_key': 'test_value', 'vars': {'test_var': 'test_value'}}

        self.assertEqual(test_data_without, RigelfileDecoder().decode(test_data_without))
        self.assertEqual(test_data_without, RigelfileDecoder().decode(test_data_with))

    def test_undeclared_variable_error_dict(self) -> None:
        """
        Test if UndeclaredGlobalVariable is thrown if references
        to unknown global variables are made inside a dict.
        """
        test_data = {'test_key': '$unknown', 'vars': {'template_var': 'test_value'}}
        with self.assertRaises(UndeclaredGlobalVariable):
            RigelfileDecoder().decode(test_data)

    def test_undeclared_variable_error_list(self) -> None:
        """
        Test if UndeclaredGlobalVariable is thrown if references
        to unknown global variables are made inside a list.
        """
        test_data = {'test_key': ['$unknown'], 'vars': {'template_var': 'test_value'}}
        with self.assertRaises(UndeclaredGlobalVariable):
            RigelfileDecoder().decode(test_data)

    def test_decoding_mechanism_dict(self) -> None:
        """
        Test if decoding mechanism works as expected whenever references
        to unknown global variables are made inside a dict.
        """
        template_value = 'test_value'
        unchanged_value = 'unchanged_value'
        test_data = {
            'vars': {'template_var': template_value},
            'test_key': '$template_var',
            'unchanged_key': unchanged_value
        }
        decoded_test_data = RigelfileDecoder().decode(test_data)
        self.assertEqual(decoded_test_data['test_key'], template_value)
        self.assertEqual(decoded_test_data['unchanged_key'], unchanged_value)  # control value

    def test_decoding_mechanism_list(self) -> None:
        """
        Test if decoding mechanism works as expected whenever references
        to unknown global variables are made inside a list.
        """
        template_value = 'test_value'
        unchanged_value = 'unchanged_value'
        test_data = {
            'vars': {'template_var': template_value},
            'test_key': ['$template_var', unchanged_value]
        }
        decoded_test_data = RigelfileDecoder().decode(test_data)
        self.assertEqual(decoded_test_data['test_key'][0], template_value)
        self.assertEqual(decoded_test_data['test_key'][1], unchanged_value)  # control value


class YAMLInjectorTesting(unittest.TestCase):
    """
    Test suite for rigel.parsers.injector.YAMLInjector class.
    """

    def test_injecting_unknown_field(self) -> None:
        """
        Test if MissingRequiredFieldError is thrown is a required field is not provided.
        """
        with self.assertRaises(MissingRequiredFieldError):
            injector = YAMLInjector(TestDataclass)
            injector.inject({})

    @patch.object(TestDataclass, '__init__')
    def test_injected_data(self, mock_dataclass: Mock) -> None:
        """
        Test if the provided data is properly forwarded to the dataclass constructor.
        """
        data = {'number': 1, 'flag': True}

        mock_dataclass.return_value = None

        injector = YAMLInjector(TestDataclass)
        injector.inject(data)

        mock_dataclass.assert_called_once_with(**data)


class RigelfileParserTesting(unittest.TestCase):
    """
    Test suite for rigel.parsers.riglefile.RigelfileParser class.
    """

    build_yaml_data: Dict[str, Any] = {
        'build': {
            'package': 'test_package',
            'distro': 'test_distro',
            'command': 'test_command',
            'image': 'test_image'
        }
    }

    file_basic_build = 'assets/build_basic'
    file_complete_build = 'assets/build_complete'

    def test_missing_build_block(self) -> None:
        """
        Test if IncompleteRigelfileError is thrown if Rigelfile misses 'build' block.
        """
        with self.assertRaises(IncompleteRigelfileError):
            RigelfileParser({})

    @patch.object(EnvironmentVariable, '__init__')
    def test_env_variables_ignored(self, mock_dataclass: Mock) -> None:
        """
        Test if no custom environment variable value is stored when field 'env' is left undeclared.
        """
        RigelfileParser(self.build_yaml_data)
        self.assertFalse(mock_dataclass.called)

    @patch.object(EnvironmentVariable, '__init__')
    def test_env_variables_creation(self, mock_dataclass: Mock) -> None:
        """
        Test if custom environment variables' values are properly stord.
        """
        yaml_data = copy.deepcopy(self.build_yaml_data)
        yaml_data['build'].update(
            {'env': [
                'TEST_VAR_1=test_var_1',
                'TEST_VAR_2=test_var_2',
                'TEST_VAR_3=test_var_3'
            ]}
        )
        mock_dataclass.return_value = None

        RigelfileParser(yaml_data)

        self.assertEqual(len(yaml_data['build']['env']), mock_dataclass.call_count)
        for env in yaml_data['build']['env']:
            name, value = env.strip().split('=')
            mock_dataclass.called_once_with(**{'name': name, 'value': value})

    @patch.object(SSHKey, '__init__')
    def test_ssh_keys_ignored(self, mock_dataclass: Mock) -> None:
        """
        Test if no SSH information is stored when field 'ssh' is left undeclared.
        """
        RigelfileParser(self.build_yaml_data)
        self.assertFalse(mock_dataclass.called)

    def test_invalid_plugin_declaration(self) -> None:
        """
        Test if an MissingRequiredFieldError is thrown when an invalid plugin is declared.
        """
        with self.assertRaises(MissingRequiredFieldError):
            yaml_data = copy.deepcopy(self.build_yaml_data)
            yaml_data.update({'deploy': [{}]})
            RigelfileParser(yaml_data)

        with self.assertRaises(MissingRequiredFieldError):
            yaml_data = copy.deepcopy(self.build_yaml_data)
            yaml_data.update({'simulate': [{}]})
            RigelfileParser(yaml_data)

    def test_module_not_found(self) -> None:
        """
        Test if PluginNotFoundError is thrown if an unknown plugin is declared.
        """
        with self.assertRaises(PluginNotFoundError):
            yaml_data = copy.deepcopy(self.build_yaml_data)
            yaml_data.update({'deploy': [{'plugin': 'unknown'}]})
            RigelfileParser(yaml_data)

        with self.assertRaises(PluginNotFoundError):
            yaml_data = copy.deepcopy(self.build_yaml_data)
            yaml_data.update({'simulate': [{'plugin': 'unknown'}]})
            RigelfileParser(yaml_data)

    @patch('rigel.parsers.rigelfile.getattr')
    @patch('rigel.parsers.rigelfile.import_module')
    @patch('rigel.parsers.rigelfile.YAMLInjector.inject')
    def test_deploy_plugin_creation(
            self,
            injector_mock: Mock,
            importlib_mock: Mock,
            getattr_mock: Mock
            ) -> None:
        """
        Test if deploy plugins are properly initialized and correctly passed their data.
        """
        deploy_plugin_name = 'test_deploy_plugin'
        module_name = 'test_module'
        plugin_class = 'PluginClass'

        yaml_data = copy.deepcopy(self.build_yaml_data)
        deploy_plugin_data = {
            'plugin': deploy_plugin_name,
            'number': 42,
            'flag': True
        }
        yaml_data.update({'deploy': [deploy_plugin_data]})

        importlib_mock.return_value = module_name
        getattr_mock.return_value = plugin_class
        injector_mock.return_value = 'PluginInstance'

        parser = RigelfileParser(yaml_data)

        importlib_mock.assert_called_once_with(deploy_plugin_name)
        getattr_mock.assert_called_once_with(module_name, 'Plugin')
        deploy_plugin_data.pop('plugin')
        injector_mock.assert_called_with(deploy_plugin_data)
        self.assertEqual(len(parser.registry_plugins), 1)

    @patch('rigel.parsers.rigelfile.getattr')
    @patch('rigel.parsers.rigelfile.import_module')
    @patch('rigel.parsers.rigelfile.YAMLInjector.inject')
    def test_simulate_plugin_creation(
            self,
            injector_mock: Mock,
            importlib_mock: Mock,
            getattr_mock: Mock
            ) -> None:
        """
        Test if simulation plugins are properly initialized and correctly passed their data.
        """
        simulate_plugin_name = 'test_simulate_plugin'
        module_name = 'test_module'
        plugin_class = 'PluginClass'

        yaml_data = copy.deepcopy(self.build_yaml_data)
        simulate_plugin_data = {
            'plugin': simulate_plugin_name,
            'number': 42,
            'flag': True
        }
        yaml_data.update({'simulate': [simulate_plugin_data]})

        importlib_mock.return_value = module_name
        getattr_mock.return_value = plugin_class
        injector_mock.return_value = 'PluginInstance'

        parser = RigelfileParser(yaml_data)

        importlib_mock.assert_called_once_with(simulate_plugin_name)
        getattr_mock.assert_called_once_with(module_name, 'Plugin')
        simulate_plugin_data.pop('plugin')
        injector_mock.assert_called_with(simulate_plugin_data)
        self.assertEqual(len(parser.simulation_plugins), 1)


if __name__ == '__main__':
    unittest.main()
