import unittest
from rigel.models.application import Package
from rigel.plugins.core.dockerfile.models import PluginModel
from rigel.plugins.core.dockerfile.renderer import Renderer
from unittest.mock import MagicMock, Mock, mock_open, patch


class RendererTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.core.dockerfile.renderer.Renderer class.
    """

    configuration_data = {
        'distro': 'test_distro',
        'command': 'test_command',
        'package': Package()
    }

    @patch('rigel.plugins.core.dockerfile.renderer.resource_string')
    @patch('rigel.plugins.core.dockerfile.renderer.Template')
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

        test_configuration = PluginModel(**self.configuration_data)
        Renderer(test_configuration).render(input_file, output_file)

        resources_mock.assert_called_once_with('rigel.plugins.core.dockerfile.renderer', f'assets/{input_file}')
        template_mock.assert_called_once_with(filepath.decode())
        open_mock.assert_called_once_with(output_file, 'w+')
        template_instance.render.assert_called_once_with(configuration=test_configuration.dict())
        open_mock.return_value.__enter__().write.assert_called_once_with(template_data)
