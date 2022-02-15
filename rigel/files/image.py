from pydantic import BaseModel, validator
from rigel.exceptions import UnsupportedCompilerError
from rigel.loggers import MessageLogger
from typing import Any, Dict, List


class EnvironmentVariable(BaseModel):
    """
    Information regarding a given environment variable and its value.

    :type name: string
    :param name: The name of the environment variable (REQUIRED).
    :type value: string
    :param name: The value of the environment variable (REQUIRED).
    """
    name: str
    value: str  # numeric values are also interpreted as text


class SSHKey(BaseModel):
    """
    Information regarding a given private SSH key.

    :type value: string
    :param value: The private SSH key (REQUIRED).
    :type hostname: string
    :param hostname: The URL of the host associated with the key (REQUIRED).
    :type file: bool
    :param file: Tell if field 'value' consists of a path or a environment variable name. Default is False.
    """
    value: str
    hostname: str
    file: bool = False


class ImageConfigurationFile(BaseModel):
    """
    Information regarding a Docker image.

    :type command: string
    :param command: The command to be executed once a container starts executing (REQUIRED).
    :type distro: string
    :param distro: The ROS distro to be used (REQUIRED).
    :type package: string
    :param package: The name of the package ROS to be containerized (REQUIRED).
    :type image: string
    :param image: The name for the final Docker image (REQUIRED).
    :type apt: List[string]
    :param apt: The name of dependencies to be installed using APT.
    :type compiler: string
    :param compiler: The tool with which to compile the containerized ROS workspace. Default value is 'catkin_make'.
    :type entrypoint: List[string]
    :param entrypoint: A list of commands to be run while executing the entrypoint script.
    :type env: List[rigel.files.EnvironmentVariable]
    :param env: A list of environment variables to be set inside the Docker image.
    :type hostname: List[string]
    :type rosinstall: List[string]
    :param rosinstall: A list of all required .rosinstall files.
    :type run: List[string]
    :param run: A list of commands to be executed while building the Docker image.
    :type ssh: List[rigel.files.SSHKey]
    :param ssh: A list of all required private SSH keys.
    :type vars: Dict[str, Any]
    :param vars: The name of custom global variables.
    """
    command: str
    distro: str
    image: str
    package: str

    apt: List[str] = []
    compiler: str = 'catkin_make'
    entrypoint: List[str] = []
    env: List[EnvironmentVariable] = []
    hostname: List[str] = []
    rosinstall: List[str] = []
    run: List[str] = []
    ssh: List[SSHKey] = []
    vars: Dict[str, Any] = {}

    def __init__(self, **data):  # type: ignore[no-untyped-def]
        envs = []
        if 'env' in data:
            for env in data['env']:
                name, value = env.strip().split('=')
                envs.append({'name': name, 'value': value})
        data['env'] = envs
        super().__init__(**data)

    @validator('compiler')
    def validate_compiler(cls, compiler):  # type: ignore[no-untyped-def]
        if compiler not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(compiler=compiler)
        return compiler

    @validator('ssh')
    def warn_unused_keys(cls, keys, values):  # type: ignore[no-untyped-def]
        if keys and not values['rosinstall']:
            MessageLogger().warning('No .rosinstall file was declared. Unused SSH keys.')
        return keys
