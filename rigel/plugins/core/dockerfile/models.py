from pydantic import BaseModel, validator
from rigel.exceptions import UnsupportedCompilerError
from rigel.models.package import Package
from typing import Any, Dict, List


class Compiler(BaseModel):

    # Optional fields
    name: str = 'catkin_make'
    cmake_args: Dict[str, str] = {}

    @validator('name')
    def validate_compiler(cls, name: str) -> str:
        """Ensure that the specified ROS package compiler used is supported by Rigel.

        :type name: string
        :param name: ROS package compiler.
        """
        print(name)
        # NOTE: At the moment only "catkin" and "colcon" are supported.
        if name not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(name)
        return name


class PluginModel(BaseModel):
    """A plugin that creates a ready-to-use Dockerfile for an existing ROS package.

    :type command: string
    :cvar command: The command to be executed once a container starts executing.
    :type distro: string
    :cvar distro: The target ROS distro. This field is automatically populated by Rigel.
    :type apt: List[string]
    :cvar apt: The name of dependencies to be installed using APT.
    :type compiler: Compiler
    :cvar compiler: The tool with which to compile the containerized ROS workspace. Default value is 'catkin_make'.
    :type entrypoint: List[string]
    :cvar entrypoint: A list of commands to be run while executing the entrypoint script.
    :type env: List[Dict[str, Any]]
    :cvar env: A list of environment variables to be set inside the Docker image.
    :type package: Package
    :cvar package: The target package identifier. This field is automatically populated by Rigel.
    :type rosinstall: List[string]
    :cvar rosinstall: A list of all required .rosinstall files.
    :type ros_image: string
    :cvar ros_image: The official ROS Docker image to use as a base for the new Docker image.
    :type docker_run: List[string]
    :cvar docker_run: A list of commands to be executed while building the Docker image.
    :type username: string
    :cvar username: The desired username. Defaults to 'user'.
    """
    # Required fields.
    command: str
    distro: str
    package: Package
    compiler: Compiler

    # Optional fields.
    apt: List[str] = []

    entrypoint: List[str] = []
    env: List[Dict[str, Any]] = []
    rosinstall: List[str] = []
    ros_image: str
    docker_run: List[str] = []
    username: str = 'rigeluser'

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        if not kwargs.get('ros_image') and kwargs.get('distro'):
            kwargs['ros_image'] = kwargs['distro']

        super().__init__(*args, **kwargs)
