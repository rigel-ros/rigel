import unittest
from rigel.files.creator import RigelfileCreator
from unittest.mock import Mock, patch


class RigelfileCreatorTesting(unittest.TestCase):
    """
    Test suite for rigel.files.RigelfileCreator class.
    """

    @patch('rigel.files.creator.resource_filename')
    @patch('rigel.files.creator.shutil.copyfile')
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

        creator = RigelfileCreator()
        creator.create()
        resources_mock.assert_called_once_with('rigel.files.creator', 'assets/Rigelfile')
        shutil_mock.assert_called_once_with(filepath, 'Rigelfile')


if __name__ == '__main__':
    unittest.main()
