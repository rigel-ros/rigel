from pydantic import Extra
from rigel.models.data import ComplexDataModel


class SSHPrivateKeyFile(ComplexDataModel, extra=Extra.forbid):
    """Information placeholder regarding a given private SSH key.

    :type hostname: string
    :cvar hostname: The URL of the host associated with the key.
    :type path: string
    :cvar path: The system path to the private SSH key.
    """

    hostname: str
    path: str


class SSHPrivateKey(ComplexDataModel, extra=Extra.forbid):

    """Information placeholder regarding a given private SSH key.

    :type hostname: string
    :cvar hostname: The URL of the host associated with the key.
    :type value: string
    :cvar value: The private SSH key.
    """

    hostname: str
    value: str
