import unittest
from io import StringIO
from rigel.exceptions import (
    EmptyRigelfileError,
    RigelError,
    RigelfileNotFound,
    UnformattedRigelfileError,
    UnsupportedCompilerError
)
from rigel.files.renderer import Renderer
from rigel.files.image import ImageConfigurationFile
from rigel.files.rigelfile import RigelfileCreator
from rigel.files.loader import YAMLDataLoader
from typing import Type
from unittest.mock import mock_open, MagicMock, Mock, patch


class RendererTesting(unittest.TestCase):
    """
    Test suite for rigel.files.dockerfile.Renderer class.
    """

    configuration_data = {
        'package': 'test_package',
        'distro': 'test_distro',
        'command': 'test_command',
        'image': 'test_image'
    }

    @patch('rigel.files.renderer.resource_string')
    @patch('rigel.files.renderer.Template')
    @patch('builtins.open', new_callable=mock_open())
    def test_renderer(
            self,
            open_mock: Mock,
            template_mock: Mock,
            resources_mock: Mock
            ) -> None:
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

        test_configuration = ImageConfigurationFile(**self.configuration_data)
        Renderer(test_configuration).render(input_file, output_file)

        resources_mock.assert_called_once_with('rigel.files.renderer', f'assets/templates/{input_file}')
        template_mock.assert_called_once_with(filepath.decode())
        open_mock.assert_called_once_with(f'.rigel_config/{output_file}', 'w+')
        template_instance.render.assert_called_once_with(configuration=test_configuration.dict())
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
    def test_rigelfile_creation(
            self,
            shutil_mock: Mock,
            resources_mock: Mock
            ) -> None:
        """
        Test if the creation of a new Rigelfile is done as expected.
        """
        filepath = 'test_path/Rigelfile'
        resources_mock.return_value = filepath

        RigelfileCreator().create()
        resources_mock.assert_called_once_with('rigel.files.rigelfile', 'assets/Rigelfile')
        shutil_mock.assert_called_once_with(filepath, 'Rigelfile')


class YAMLDataLoaderTesting(unittest.TestCase):
    """
    Test suite for rigel.files.loader.YAMLDataLoader class.
    """

    def __base_error_test(self, error: Type[RigelError], content: str, open_mock: Mock) -> None:
        """
        Test if a specific error is thrown when parsing a given YAML data.
        """
        open_mock.return_value = StringIO(content)
        with self.assertRaises(error):

            filename = 'invalid_file'
            YAMLDataLoader(filename).load()
            open_mock.assert_called_once_with(filename, 'r')

    def test_loading_not_found(self) -> None:
        """
        Test if RigelfileNotFound is thrown if an Rigelfile does not exist.
        """
        with self.assertRaises(RigelfileNotFound):
            YAMLDataLoader('./unexistent_file').load()

    @patch('builtins.open', new_callable=mock_open())
    def test_empty_rigelfile(self, open_mock: Mock) -> None:
        """
        Test if EmptyRigelfileError is thrown if Rigelfile contains no data.
        """
        self.__base_error_test(EmptyRigelfileError, '', open_mock)

    @patch('builtins.open', new_callable=mock_open())
    def test_unformatted_rigelfile(self, open_mock: Mock) -> None:
        """
        Test if UnformattedRigelfileError is thrown if Rigelfile is not properly formatted.
        """
        self.__base_error_test(UnformattedRigelfileError, ':', open_mock)


if __name__ == '__main__':
    unittest.main()
