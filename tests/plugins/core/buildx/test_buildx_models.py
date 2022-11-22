import unittest
from rigel.exceptions import UnsupportedPlatformError
from rigel.models.package import Package
from rigel.plugins.core.buildx.models import PluginModel


class BuildXPluginModelTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.core.buildx.models.PluginModel class.
    """

    def test_unsupported_platform_error(self) -> None:
        """
        Ensure that an instance of UnsupportedPlatformError is thrown if an unsupported
        plaform is specified.
        """
        test_distro = 'bits/bytes42'

        with self.assertRaises(UnsupportedPlatformError) as context:
            PluginModel(
                distro='test_distro',
                image='test_image',
                package='test_package',
                platforms=[test_distro]
            )
        self.assertEqual(context.exception.kwargs['platform'], test_distro)

    def test_default_values(self) -> None:
        """
        Ensure that an PluginModel instances are created with expected default values.
        """
        test_distro = 'test_distro'
        test_image = 'test_image'
        test_package = Package()

        plugin = PluginModel(
            distro='test_distro',
            image='test_image',
            package=test_package
        )

        self.assertEqual(plugin.distro, test_distro)
        self.assertEqual(plugin.image, test_image)
        self.assertEqual(plugin.package, test_package)

        self.assertEqual(plugin.buildargs, {})
        self.assertEqual(plugin.load, False)
        self.assertEqual(plugin.platforms, [])
        self.assertEqual(plugin.push, False)
        self.assertEqual(plugin.registry, None)


if __name__ == '__main__':
    unittest.main()
