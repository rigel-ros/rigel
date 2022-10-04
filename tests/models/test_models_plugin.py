import unittest
from rigel.exceptions import (
    InvalidPluginNameError
)
from rigel.models import PluginSection


class PluginSectionTesting(unittest.TestCase):
    """
    Test suite for rigel.models.DockerSection class.
    """

    def test_invalid_plugin_name_error(self) -> None:
        """
        Test if InvalidPluginName is thrown if an invalid plugin name is provided.
        """
        invalid_plugin_name = 'invalid_plugin_name'
        plugin_data = {'name': invalid_plugin_name}
        with self.assertRaises(InvalidPluginNameError) as context:
            PluginSection(**plugin_data)
        self.assertEqual(context.exception.kwargs['plugin'], invalid_plugin_name)


if __name__ == '__main__':
    unittest.main()
