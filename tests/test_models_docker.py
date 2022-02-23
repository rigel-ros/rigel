import unittest
from rigelcore.exceptions import (
    UndeclaredEnvironmentVariableError
)
from rigel.exceptions import (
    UnsupportedCompilerError
)
from rigel.models import DockerSection, SSHKey
from unittest.mock import Mock, patch


class SSHKeyModelTesting(unittest.TestCase):
    """
    Test suite for rigel.models.SSHKey class
    """

    @patch('rigel.models.docker.os.environ.get')
    def test_undeclared_environment_variable_error(self, environ_mock: Mock) -> None:
        """
        Test if UndeclaredEnvironmentVariableError is thrown if an undeclared
        environment variable is declared.
        """
        test_environment_variable = 'TEST_ENVIRONMENT_VARIABLE'
        test_key_data = {
            'hostname': 'test_hostname',
            'value': test_environment_variable,
            'file': False
        }

        environ_mock.return_value = None
        with self.assertRaises(UndeclaredEnvironmentVariableError) as context:
            SSHKey(**test_key_data)

        environ_mock.assert_called_once_with(test_environment_variable)
        self.assertEqual(context.exception.kwargs['env'], test_environment_variable)


class DockerSectionTesting(unittest.TestCase):
    """
    Test suite for rigel.models.DockerSection class.
    """

    def test_unsupported_compiler_error(self) -> None:
        """
        Test if UnsupportedCompilerError is thrown if an unsupported compiler is declared.
        """
        compiler = 'invalid_compiler'
        data = {
            'command': 'test-command',
            'distro': 'test-distro',
            'image': 'test-image',
            'package': 'test-package',
            'compiler': compiler
        }
        with self.assertRaises(UnsupportedCompilerError) as context:
            DockerSection(**data)
        self.assertEqual(context.exception.kwargs['compiler'], compiler)


if __name__ == '__main__':
    unittest.main()
