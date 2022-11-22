import unittest
from rigel.exceptions import UndeclaredEnvironmentVariableError
from rigel.models.package import SSHKey
from unittest.mock import Mock, patch


class SSHKeyModelTesting(unittest.TestCase):
    """
    Test suite for rigel.models.SSHKey class
    """

    @patch('rigel.models.package.os.environ.get')
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
        self.assertEqual(context.exception.env, test_environment_variable)


if __name__ == '__main__':
    unittest.main()
