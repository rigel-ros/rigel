import unittest
from rigel.exceptions import (
    UnsupportedCompilerError,
    UnsupportedPlatformError
)
from rigel.models import DockerSection


class DockerSectionTesting(unittest.TestCase):
    """
    Test suite for rigel.models.DockerSection class.
    """

    def test_default_ros_image(self) -> None:
        """
        Test if by default the ROS Docker image used as a base for new images matches the
        selected ROS distribution.
        """
        test_distro = 'test_ros_distro'
        data = {
            'command': 'test-command',
            'distro': test_distro,
            'image': 'test-image',
            'package': 'test-package'
        }
        section = DockerSection(**data)
        self.assertEqual(section.distro, test_distro)
        self.assertEqual(section.ros_image, test_distro)

    def test_custom_ros_image(self) -> None:
        """
        Test if the mechanism to declare custom base ROS Docker images works as expected.
        """
        test_distro = 'test_ros_distro'
        test_ros_image = 'test_ros_image'
        data = {
            'command': 'test-command',
            'distro': test_distro,
            'image': 'test-image',
            'package': 'test-package',
            'ros_image': test_ros_image
        }
        section = DockerSection(**data)
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
            'image': 'test-image',
            'package': 'test-package',
            'compiler': compiler
        }
        with self.assertRaises(UnsupportedCompilerError) as context:
            DockerSection(**data)
        self.assertEqual(context.exception.kwargs['compiler'], compiler)

    def test_unsupported_platform_error(self) -> None:
        """
        Test if UnsupportedPlatformError is thrown if an invalid platform is declared.
        """
        platform = 'test_unsupported_platform'
        data = {
            'command': 'test-command',
            'distro': 'test-distro',
            'image': 'test-image',
            'package': 'test-package',
            'platforms': [platform]
        }

        with self.assertRaises(UnsupportedPlatformError) as context:
            DockerSection(**data)
        self.assertEqual(context.exception.kwargs['platform'], platform)


if __name__ == '__main__':
    unittest.main()
