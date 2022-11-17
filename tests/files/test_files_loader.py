import unittest
from rigel.exceptions import (
    EmptyRigelfileError,
    RigelfileNotFoundError,
    UnformattedRigelfileError
)
from rigel.files.loader import YAMLDataLoader
from unittest.mock import Mock, mock_open, patch


class YAMLDataLoaderTesting(unittest.TestCase):
    """
    Test suite for rigel.files.YAMLDataLoader class.
    """

    def test_rigelfile_not_found_error(self) -> None:
        """
        Test if RigelfileNotFoundError is thrown if an Rigelfile does not exist.
        """
        with self.assertRaises(RigelfileNotFoundError):
            loader = YAMLDataLoader('./unexistent_file')
            loader.load()

    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_empty_rigelfile_error(self, open_mock: Mock) -> None:
        """
        Test if EmptyRigelfileError is thrown if Rigelfile contains no data.
        """
        filename = 'invalid_rigelfile'
        with self.assertRaises(EmptyRigelfileError):
            loader = YAMLDataLoader(filename)
            loader.load()
        open_mock.assert_called_once_with(filename, 'r')

    @patch('builtins.open',  new_callable=mock_open, read_data=':')
    def test_unformatted_rigelfile_error(self, open_mock: Mock) -> None:
        """
        Test if UnformattedRigelfileError is thrown if Rigelfile is not properly formatted.
        """
        filename = 'invalid_rigelfile'
        with self.assertRaises(UnformattedRigelfileError):
            loader = YAMLDataLoader(filename)
            loader.load()
        open_mock.assert_called_once_with(filename, 'r')


if __name__ == '__main__':
    unittest.main()
