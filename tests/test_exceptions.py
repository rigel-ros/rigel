import unittest
from rigel.exceptions import (
    EmptyRigelfileError,
    IncompleteRigelfileError,
    InvalidPluginNameError,
    InvalidValueError,
    MissingRequiredFieldError,
    NotAModuleError,
    PluginInstallationError,
    PluginNotCompliantError,
    PluginNotFoundError,
    RigelfileAlreadyExistsError,
    RigelfileNotFoundError,
    UndeclaredEnvironmentVariableError,
    UndeclaredGlobalVariableError,
    UndeclaredValueError,
    UnformattedRigelfileError,
    UnsupportedCompilerError
)


class ExceptionTesting(unittest.TestCase):
    """
    Test suite for all classes declared in rigel.exceptions.
    """

    def test_rigelfile_not_found_error(self) -> None:
        """
        Ensure that instances of RigelfileNotFoundError are thrown as expected.
        """
        err = RigelfileNotFoundError()
        self.assertEqual(err.code, 6)

    def test_rigelfile_already_exists_error(self) -> None:
        """
        Ensure that instances of RigelfileAlreadyExistsError are thrown as expected.
        """
        err = RigelfileAlreadyExistsError()
        self.assertEqual(err.code, 7)

    def test_unformatted_rigelfile_error(self) -> None:
        """
        Ensure that instances of UnformattedRigelfileError are thrown as expected.
        """
        test_trace = 'test_trace'
        err = UnformattedRigelfileError(trace=test_trace)
        self.assertEqual(err.code, 8)
        self.assertEqual(err.kwargs['trace'], test_trace)

    def test_incomplete_rigelfile_error(self) -> None:
        """
        Ensure that instances of IncompleteRigelfileError are thrown as expected.
        """
        test_block = 'test_block'
        err = IncompleteRigelfileError(block=test_block)
        self.assertEqual(err.code, 9)
        self.assertEqual(err.kwargs['block'], test_block)

    def test_undeclared_value_error(self) -> None:
        """
        Ensure that instances of UndeclaredValueError are thrown as expected.
        """
        test_field = 'test_field'
        err = UndeclaredValueError(field=test_field)
        self.assertEqual(err.code, 10)
        self.assertEqual(err.kwargs['field'], test_field)

    def test_invalid_value_error(self) -> None:
        """
        Ensure that instances of InvalidValueError are thrown as expected.
        """
        test_instance_type = str
        test_field = 'test_field'
        err = InvalidValueError(instance_type=test_instance_type, field=test_field)
        self.assertEqual(err.code, 11)
        self.assertEqual(err.kwargs['instance_type'], test_instance_type)
        self.assertEqual(err.kwargs['field'], test_field)

    def test_empty_rigelfile_error(self) -> None:
        """
        Ensure that instances of EmptyRigelfileError are thrown as expected.
        """
        err = EmptyRigelfileError()
        self.assertEqual(err.code, 12)

    def test_unsupported_compiler_error(self) -> None:
        """
        Ensure that instances of UnsupportedCompilerError are thrown as expected.
        """
        test_compiler = 'test_compiler'
        err = UnsupportedCompilerError(compiler=test_compiler)
        self.assertEqual(err.code, 13)
        self.assertEqual(err.kwargs['compiler'], test_compiler)

    def test_missing_required_field_error(self) -> None:
        """
        Ensure that instances of MissingRequiredFieldError are thrown as expected.
        """
        test_field = 'test_field'
        err = MissingRequiredFieldError(field=test_field)
        self.assertEqual(err.code, 14)
        self.assertEqual(err.kwargs['field'], test_field)

    def test_undeclared_environment_variable_error(self) -> None:
        """
        Ensure that instances of UndeclaredEnvironmentVariableError are thrown as expected.
        """
        test_env = 'TEST_ENV'
        err = UndeclaredEnvironmentVariableError(env=test_env)
        self.assertEqual(err.code, 15)
        self.assertEqual(err.kwargs['env'], test_env)

    def test_undeclared_global_variable_error(self) -> None:
        """
        Ensure that instances of UndeclaredGlobalVariableError are thrown as expected.
        """
        test_field = 'test_field'
        test_var = 'test_var'
        err = UndeclaredGlobalVariableError(field=test_field, var=test_var)
        self.assertEqual(err.code, 16)
        self.assertEqual(err.kwargs['field'], test_field)
        self.assertEqual(err.kwargs['var'], test_var)

    def test_plugin_not_found_error(self) -> None:
        """
        Ensure that instances of PluginNotFoundError are thrown as expected.
        """
        test_plugin = 'test_plugin'
        err = PluginNotFoundError(plugin=test_plugin)
        self.assertEqual(err.code, 17)
        self.assertEqual(err.kwargs['plugin'], test_plugin)

    def test_plugin_installation_error(self) -> None:
        """
        Ensure that instances of PluginInstallationError are thrown as expected.
        """
        test_plugin = 'test_plugin'
        err = PluginInstallationError(plugin=test_plugin)
        self.assertEqual(err.code, 18)
        self.assertEqual(err.kwargs['plugin'], test_plugin)

    def test_plugin_not_compliant_error(self) -> None:
        """
        Ensure that instances of PluginNotCompliantError are thrown as expected.
        """
        test_plugin = 'test_plugin'
        test_cause = 'test_cause'
        err = PluginNotCompliantError(plugin=test_plugin, cause=test_cause)
        self.assertEqual(err.code, 19)
        self.assertEqual(err.kwargs['plugin'], test_plugin)
        self.assertEqual(err.kwargs['cause'], test_cause)

    def test_not_a_module_error(self) -> None:
        """
        Ensure that instances of NotAModuleError are thrown as expected.
        """
        test_instance_type = str
        err = NotAModuleError(instance_type=test_instance_type)
        self.assertEqual(err.code, 20)
        self.assertEqual(err.kwargs['instance_type'], test_instance_type)

    def invalid_plugin_name_error(self) -> None:
        """
        Ensure that instances of InvalidPluginNameError are thrown as expected.
        """
        test_plugin = 'test_plugin'
        err = InvalidPluginNameError(plugin=test_plugin)
        self.assertEqual(err.code, 21)
        self.assertEqual(err.kwargs['plugin'], test_plugin)


if __name__ == '__main__':
    unittest.main()
