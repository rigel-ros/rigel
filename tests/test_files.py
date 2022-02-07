import unittest
from rigel.exceptions import (
    RigelfileNotFound,
    UnsupportedCompilerError
)
from rigel.files.image import ImageConfigurationFile
from rigel.files.loader import YAMLDataLoader


class ImageConfigurationFileTesting(unittest.TestCase):
    """
    Test suite for rigel.files.image.ImageConfigurationFile class.
    """

    def test_invalid_compiler(self) -> None:
        """
        Test if UnsupportedCompilerError is thrown if an unsupported compiler is used.
        """
        data = {
            'command': 'test-command',
            'distro': 'test-distro',
            'image': 'test-image',
            'package': 'test-package',
            'compiler': 'test-compiler'
        }
        with self.assertRaises(UnsupportedCompilerError):
            ImageConfigurationFile(**data)


class YAMLDataLoaderTesting(unittest.TestCase):
    """
    Test suite for rigel.files.loader.YAMLDataLoader class.
    """

    def test_loading_not_found(self) -> None:
        """
        Test if RigelfileNotFound is thrown if an Rigelfile does not exist.
        """
        with self.assertRaises(RigelfileNotFound):
            YAMLDataLoader.load_data('./unexistent_file')


if __name__ == '__main__':
    unittest.main()
