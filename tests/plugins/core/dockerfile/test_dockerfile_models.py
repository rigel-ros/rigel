import unittest
from rigel.exceptions import UnsupportedCompilerError
from rigel.models.package import Package
from rigel.plugins.core.dockerfile.models import PluginModel


class DockerfilePluginModelTesting(unittest.TestCase):
    """
    Test suite for rigel.plugins.core.dockerfile.models.PluginModel class.
    """

    def test_default_values(self) -> None:
        """
        Test if default values are set as expected.
        """
        test_command = 'test_command'
        test_distro = 'test_ros_distro'
        test_package = Package()
        data = {
            'command': test_command,
            'distro': test_distro,
            'package': test_package
        }
        section = PluginModel(**data)
        self.assertEqual(section.command, test_command)
        self.assertEqual(section.distro, test_distro)
        self.assertEqual(section.package, test_package)

        self.assertEqual(section.apt, [])
        self.assertEqual(section.compiler, 'catkin_make')
        self.assertEqual(section.entrypoint, [])
        self.assertEqual(section.env, [])
        self.assertEqual(section.rosinstall, [])
        self.assertEqual(section.ros_image, test_distro)
        self.assertEqual(section.docker_run, [])
        self.assertEqual(section.username, 'rigeluser')

    def test_custom_ros_image(self) -> None:
        """
        Test if the mechanism to declare custom base ROS Docker images works as expected.
        """
        test_distro = 'test_ros_distro'
        test_ros_image = 'test_ros_image'
        data = {
            'command': 'test-command',
            'distro': test_distro,
            'package': Package(),
            'ros_image': test_ros_image
        }
        section = PluginModel(**data)
        self.assertEqual(section.distro, test_distro)
        self.assertEqual(section.ros_image, test_ros_image)

    def test_unsupported_compiler_error(self) -> None:
        """
        Test if UnsupportedCompilerError is thrown if an unsupported compiler is declared.
        """
        compiler = 'invalid_compiler'
        data = {
            'command': 'test-command',
            'distro': 'test-distro',
            'package': Package(),
            'compiler': compiler
        }
        with self.assertRaises(UnsupportedCompilerError) as context:
            PluginModel(**data)
        self.assertEqual(context.exception.compiler, compiler)


if __name__ == '__main__':
    unittest.main()
