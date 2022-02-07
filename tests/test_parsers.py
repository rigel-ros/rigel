import unittest
from dataclasses import dataclass
from rigel.exceptions import (
    IncompleteRigelfileError,
    MissingRequiredFieldError,
    UnknownFieldError
)
from rigel.parsers.injector import YAMLInjector
from rigel.parsers.rigelfile import RigelfileParser
from unittest.mock import Mock


@dataclass
class TestDataclass:
    number: int
    flag: bool


class YAMLInjectorTesting(unittest.TestCase):
    """
    Test suite for rigel.parsers.injector.YAMLInjector class.
    """

    def test_injecting_unknown_field(self) -> None:
        """
        Test if MissingRequiredFieldError is thrown is a required field is not provided.
        """
        with self.assertRaises(MissingRequiredFieldError):
            YAMLInjector.inject(TestDataclass, {})

    def test_injecting_missing_field(self) -> None:
        """
        Test if UnknownFieldError is thrown if a required field is not provided.
        """
        with self.assertRaises(UnknownFieldError):
            YAMLInjector.inject(TestDataclass, {
                'number': 1,
                'flag': True,
                'sentence': "Field 'sentence' is unknown."
            })

    def test_injected_data(self) -> None:
        """
        Test if the provided data is properly forwarded to the dataclass constructor.
        """
        data = {'number': 1, 'flag': True}
        mock = YAMLInjector.inject(Mock, data)
        self.assertEquals(mock.number, 2)


class ParserTesting(unittest.TestCase):
    """
    Test suite for rigel.parsers.riglefile.RigelfileParser class.
    """

    def test_missing_build_block(self):
        """
        Test if IncompleteRigelfileError is thrown if Rigelfile misses 'build' block.
        """
        with self.assertRaises(IncompleteRigelfileError):
            RigelfileParser({})

    # TODO: Test separate segment parsers using several configuration files.


if __name__ == '__main__':
    unittest.main()
