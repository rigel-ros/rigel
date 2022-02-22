import os
from pydantic import BaseModel, validator
from rigel.exceptions import (
    UndeclaredEnvironmentVariableError,
    UnsupportedCompilerError
)
from typing import Any, Dict, List


class SSHKey(BaseModel):
    """
    Information regarding a given private SSH key.

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
        """
        Ensure that all environment variables have a value.

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


class DockerSection(BaseModel):
    """
    A placeholder for information regarding how to containerize a ROS application using Docker.

    :type command: string
    :cvar command: The command to be executed once a container starts executing.
    :type distro: string
    :cvar distro: The ROS distro to be used.
    :type package: string
    :cvar package: The name of the package ROS to be containerized.
    :type image: string
    :cvar image: The name for the final Docker image.
    :type apt: List[string]
    :cvar apt: The name of dependencies to be installed using APT.
    :type compiler: string
    :cvar compiler: The tool with which to compile the containerized ROS workspace. Default value is 'catkin_make'.
    :type entrypoint: List[string]
    :cvar entrypoint: A list of commands to be run while executing the entrypoint script.
    :type env: List[Dict[str, Any]]
    :cvar env: A list of environment variables to be set inside the Docker image.
    :type hostname: List[string]
    :type rosinstall: List[string]
    :cvar rosinstall: A list of all required .rosinstall files.
    :type run: List[string]
    :cvar run: A list of commands to be executed while building the Docker image.
    :type ssh: List[rigel.files.SSHKey]
    :cvar ssh: A list of all required private SSH keys.
    """
    # Required fields.
    command: str
    distro: str
    image: str
    package: str

    # Optional fields.
    apt: List[str] = []
    compiler: str = 'catkin_make'
    entrypoint: List[str] = []
    env: List[Dict[str, Any]] = []
    hostname: List[str] = []
    rosinstall: List[str] = []
    run: List[str] = []
    ssh: List[SSHKey] = []

    @validator('compiler')
    def validate_compiler(cls, compiler: str) -> str:
        """
        Ensure that the specified ROS package compiler used is supported by Rigel.

        :type compiler: string
        :param compiler: ROS package compiler.
        """
        # NOTE: At the moment only "catkin" and "colcon" are supported.
        if compiler not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(compiler=compiler)
        return compiler
