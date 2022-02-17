from pydantic import BaseModel, validator
from rigel.exceptions import UnsupportedCompilerError
from typing import Any, Dict, List


class SSHKey(BaseModel):
    """
    Information regarding a given private SSH key.

    :type value: string
    :cvar value: The private SSH key.
    :type hostname: string
    :cvar hostname: The URL of the host associated with the key.
    :type file: bool
    :cvar file: Tell if field 'value' consists of a path or a environment variable name. Default is False.
    """
    value: str
    hostname: str
    file: bool = False


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
