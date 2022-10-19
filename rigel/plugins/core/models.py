import os
from pydantic import BaseModel, validator
from rigel.exceptions import UndeclaredEnvironmentVariableError
from typing import Any, Dict


class SSHKey(BaseModel):
    """Information placeholder regarding a given private SSH key.

    :type hostname: string
    :cvar hostname: The URL of the host associated with the key.
    :type value: string
    :cvar value: The private SSH key.
    :type file: bool
    :cvar file: Tell if field 'value' consists of a path or a environment variable name. Default is False.
    """

    # NOTE: the validator for field 'value' assumes field 'file' to be already defined.
    # Therefore ensure that field 'file' is always declared before
    # field 'value' in the following list.

    file: bool = False
    hostname: str
    value: str

    @validator('value')
    def ensure_valid_value(cls, v: str, values: Dict[str, Any]) -> str:
        """Ensure that all environment variables have a value.

        :type v: string
        :param v: The value for this SSH key.
        :type values: Dict[str, Any]
        :param values: This model data.
        :rtype: string
        :return: The value for this SSH key.
        """
        if not values['file']:  # ensure value concerns an environment variable
            if not os.environ.get(v):
                raise UndeclaredEnvironmentVariableError(env=v)
        return v


class Registry(BaseModel):
    """Information placeholder about an image registry.

    :type password: string
    :cvar password: The password for authentication.
    :type server: string
    :cvar server: The image registry to authenticate with.
    :type username: string
    :cvar username: The username to authenticate.
    """
    password: str
    server: str
    username: str
