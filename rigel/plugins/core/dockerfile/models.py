from pydantic import BaseModel, Extra, validator
from rigel.exceptions import UnsupportedCompilerError
from typing import Any, Dict, List


class Compiler(BaseModel, extra=Extra.forbid):

    # Optional fields
    name: str = 'catkin_make'
    cmake_args: Dict[str, str] = {}

    @validator('name')
    def validate_compiler(cls, name: str) -> str:
        """Ensure that the specified ROS package compiler used is supported by Rigel.

        :type name: string
        :param name: ROS package compiler.
        """
        # NOTE: At the moment only "catkin" and "colcon" are supported.
        if name not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(name)
        return name


class PluginModel(BaseModel, extra=Extra.forbid):
    """A plugin that creates a ready-to-use Dockerfile for an existing ROS package.

    :type command: string
    :cvar command: The command to be executed once a container starts executing.
    :type apt: List[string]
    :cvar apt: The name of dependencies to be installed using APT.
    :type compiler: Compiler
    :cvar compiler: The tool with which to compile the containerized ROS workspace. Default value is 'catkin_make'.
    :type entrypoint: List[string]
    :cvar entrypoint: A list of commands to be run while executing the entrypoint script.
    :type env: List[Dict[str, Any]]
    :cvar env: A list of environment variables to be set inside the Docker image.
    :type rosinstall: List[string]
    :cvar rosinstall: A list of all required .rosinstall files.
    :type ros_image: string
    :cvar ros_image: The official ROS Docker image to use as a base for the new Docker image.
    :type docker_run: List[string]
    :cvar docker_run: A list of commands to be executed while building the Docker image.
    :type username: string
    :cvar username: The desired username. Defaults to 'user'.
    """
    # Optional fields.
    compiler: Compiler
    command: str = ''
    apt: List[str] = []

    entrypoint: List[str] = []
    env: List[Dict[str, Any]] = []
    rosinstall: List[str] = []
    ros_image: str
    docker_run: List[str] = []
    username: str = 'rigeluser'

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        if not kwargs.get('ros_image'):
            kwargs['ros_image'] = f'ros:{kwargs["distro"]}'
        del kwargs['distro']

        super().__init__(*args, **kwargs)
