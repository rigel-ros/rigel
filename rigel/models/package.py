import os
from pydantic import BaseModel, validator
from rigel.exceptions import UndeclaredEnvironmentVariableError
from typing import Any, List, Dict
from .plugin import PluginSection


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


class Package(BaseModel):
    """A placeholder for information regarding a single Rigel-ROS package.

    Each Rigel-ROS package may support the execution of individual jobs.

    :type dir: string
    :cvar dir: The folder containing the ROS package source code, if any.
    :type jobs: Dict[str, List[PluginSection]]
    :cvar jobs: The jobs supported by the package.
    :type ssh: List[rigel.files.SSHKey]
    :cvar ssh: A list of all required private SSH keys.
    """
    # Required fields.
    name: str

    # Optional fields.
    dir: str = '.'
    jobs: Dict[str, List[PluginSection]] = {}
    ssh: List[SSHKey] = []
