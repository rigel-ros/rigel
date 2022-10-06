import unittest

from botocore.exceptions import BotoCoreError
from boto3.exceptions import Boto3Error
from rigel.exceptions import RigelError
from rigel.plugins.core.registry_plugin.exceptions import AWSBotoError


class ExceptionTesting(unittest.TestCase):
    """
    Test suite for all classes under ecr_rigel_plugin.exceptions.
    """

    def test_aws_botocore_error(self) -> None:
        """
        Ensure that instances of AWSBotoError are thrown as expected
        when a 'botocore' API call fails.
        """
        test_exception = BotoCoreError()
        err = AWSBotoError(exception=test_exception)
        self.assertEqual(err.kwargs['exception'], test_exception)
        self.assertEqual(err.code, 50)
        self.assertTrue(isinstance(err, RigelError))

    def test_aws_boto3_error(self) -> None:
        """
        Ensure that instances of AWSBotoError are thrown as expected
        when a 'boto3' API call fails.
        """
        test_exception = Boto3Error()
        err = AWSBotoError(exception=test_exception)
        self.assertEqual(err.kwargs['exception'], test_exception)
        self.assertEqual(err.code, 50)
        self.assertTrue(isinstance(err, RigelError))


if __name__ == '__main__':
    unittest.main()
