import unittest
from dataclasses import asdict, dataclass
from io import StringIO
from unittest.mock import mock_open, MagicMock, patch
from rigel.exceptions import (
    EmptyRigelfileError,
    RigelError,
    RigelfileNotFound,
    UndeclaredValueError,
    UnformattedRigelfileError,
    UnsupportedCompilerError
)
from rigel.files.renderer import Renderer
from rigel.files.image import ImageConfigurationFile
from rigel.files.rigelfile import RigelfileCreator
from rigel.files.loader import YAMLDataLoader
from unittest.mock import Mock


@dataclass
class TestFileConfiguration:
    message: str


class RendererTesting(unittest.TestCase):
    """
    Test suite for rigel.files.dockerfile.Renderer class.
    """

    @patch('rigel.files.renderer.resource_string')
    @patch('rigel.files.renderer.Template')
    @patch('builtins.open', new_callable=mock_open())
    def test_renderer(self, open_mock, template_mock, resources_mock) -> None:
        """
        Test if the mechanism to render template files works as expected.
        """
        input_file = 'TestTemplate.j2'
        output_file = 'test_rendered_file'

        filepath = f'test_path/{input_file}'.encode()
        resources_mock.return_value = filepath

        template = 'Template'
        template_data = 'File content.'

        template_instance = MagicMock()
        template_instance.return_value = template
        template_instance.render.return_value = template_data
        template_mock.return_value = template_instance

        test_configuration = TestFileConfiguration(message='test')
        Renderer.render(test_configuration, input_file, output_file)

        resources_mock.assert_called_once_with('rigel.files.renderer', f'assets/templates/{input_file}')
        template_mock.assert_called_once_with(filepath.decode())
        open_mock.assert_called_once_with(f'.rigel_config/{output_file}', 'w+')
        template_instance.render.assert_called_once_with(configuration=asdict(test_configuration))
        open_mock.return_value.__enter__().write.assert_called_once_with(template_data)


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


class RigelfileCreatorTesting(unittest.TestCase):
    """
    Test suite for rigel.files.rigelfile.RigelfileCreator class.
    """

    @patch('rigel.files.rigelfile.resource_filename')
    @patch('rigel.files.rigelfile.shutil.copyfile')
    def test_rigelfile_creation(self, shutil_mock, resources_mock) -> None:
        """
        Test if the creation of a new Rigelfile is done as expected.
        """
        filepath = 'test_path/Rigelfile'
        resources_mock.return_value = filepath

        RigelfileCreator.create()
        resources_mock.assert_called_once_with('rigel.files.rigelfile', 'assets/Rigelfile')
        shutil_mock.assert_called_once_with(filepath, 'Rigelfile')


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

    def __base_error_test(self, error: RigelError, content: str, open_mock: Mock) -> None:
        """
        Test if a specific error is thrown when parsing a given YAML data.
        """
        open_mock.return_value = StringIO(content)
        with self.assertRaises(error):

            filename = 'invalid_file'
            YAMLDataLoader.load_data(filename)
            open_mock.assert_called_once_with(filename, 'r')

    @patch('builtins.open', new_callable=mock_open())
    def test_undeclared_value(self, open_mock) -> None:
        """
        Test if UndeclaredValueError is thrown if a Rigelfile field is declared but left undefined.
        """
        self.__base_error_test(UndeclaredValueError, 'field:', open_mock)

    @patch('builtins.open', new_callable=mock_open())
    def test_empty_rigelfile(self, open_mock) -> None:
        """
        Test if EmptyRigelfileError is thrown if Rigelfile contains no data.
        """
        self.__base_error_test(EmptyRigelfileError, '', open_mock)

    @patch('builtins.open', new_callable=mock_open())
    def test_unformatted_rigelfile(self, open_mock) -> None:
        """
        Test if UnformattedRigelfileError is thrown if Rigelfile is not properly formatted.
        """
        self.__base_error_test(UnformattedRigelfileError, ':', open_mock)


if __name__ == '__main__':
    unittest.main()
