import unittest
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError,
    UnformattedRigelfileError,
    UnsupportedCompilerError,
    UnsupportedPlatformError
)


class ExceptionTesting(unittest.TestCase):
    """
    Test suite for all classes declared in rigel.exceptions.
    """

    def test_unformatted_rigelfile_error(self) -> None:
        """
        Ensure that instances of UnformattedRigelfileError are thrown as expected.
        """
        test_trace = 'test_trace'
        err = UnformattedRigelfileError(test_trace)
        self.assertEqual(err.trace, test_trace)

    def test_unsupported_compiler_error(self) -> None:
        """
        Ensure that instances of UnsupportedCompilerError are thrown as expected.
        """
        test_compiler = 'test_compiler'
        err = UnsupportedCompilerError(test_compiler)
        self.assertEqual(err.compiler, test_compiler)

    def test_unsupported_platform_error(self) -> None:
        """
        Ensure that instances of UnsupportedPlatformError are thrown as expected.
        """
        test_unsupported_platform = 'test_platform'
        err = UnsupportedPlatformError(test_unsupported_platform)
        self.assertEqual(err.platform, test_unsupported_platform)

    def test_plugin_not_found_error(self) -> None:
        """
        Ensure that instances of PluginNotFoundError are thrown as expected.
        """
        test_plugin = 'test_plugin'
        err = PluginNotFoundError(test_plugin)
        self.assertEqual(err.plugin, test_plugin)

    def test_plugin_not_compliant_error(self) -> None:
        """
        Ensure that instances of PluginNotCompliantError are thrown as expected.
        """
        test_plugin = 'test_plugin'
        test_cause = 'test_cause'
        err = PluginNotCompliantError(test_plugin, test_cause)
        self.assertEqual(err.plugin, test_plugin)
        self.assertEqual(err.cause, test_cause)


if __name__ == '__main__':
    unittest.main()
