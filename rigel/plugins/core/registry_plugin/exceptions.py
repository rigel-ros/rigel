from rigel.exceptions import RigelError


class AWSBotoError(RigelError):
    """
    Raised wheneve an error occurs while making 'boto' API calls.

    :type exception: Union[botocore.exceptions.BotoCoreError, boto3.exceptions.Boto3Error]
    :type exception: The exception thrown by the API call.
    """
    base = "An error occurred: {exception}"
    code = 50
