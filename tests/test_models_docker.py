import unittest
from rigel.exceptions import (
    UnsupportedCompilerError
)
from rigel.models import DockerSection


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
