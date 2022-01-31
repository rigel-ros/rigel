import sys
from dataclasses import dataclass, field
from typing import List


@dataclass
class EnvironmentVariable:
    """
    Information regarding a given environment variable and its value.

    :type name: string
    :param name: The name of the environment variable (REQUIRED).
    :type value: string
    :param name: The value of the environment variable (REQUIRED).
    """
    name: str
    value: str  # numeric values are also interpreted as text


@dataclass
class SSHKey:
    """
    Information regarding a given private SSH key.

    :type value: string
    :param value: The private SSH key (REQUIRED).
    :type hostname: string
    :param hostname: The URL of the host associated with the key (REQUIRED).
    :type file: bool
    :param file: Whether or not the value of 'value' consists of a path or a environment variable name. Default value is False.
    """
    value: str
    hostname: str

    file: bool = field(default_factory=lambda: False)


@dataclass
class ImageConfigurationFile:
    """
    Information regarding a Docker image.

    :type command: string
    :param command: The command to be executed once a container starts executing (REQUIRED).
    :type distro: string
    :param distro: The ROS distro to be used (REQUIRED).
    :type package: string
    :param package: The name of the package ROS to be containerized (REQUIRED).
    :type apt: list
    :param apt: The name of dependencies to be installed using APT.
    :type compiler: string
    :param compiler: The tool with which to compile the containerized ROS workspace. Default value is 'catkin_make'.
    :type entrypoint: list
    :param entrypoint: A list of commands to be run while executing the entrypoint script.
    :type env: list
    :param env: A list of environment variables to be set inside the Docker image.
    :type hostname: list
    :type rosinstall: list
    :param rosinstall: A list of all required .rosinstall files.
    :type run: list
    :param run: A list of command to be executed while building the Docker image.
    :type ssh: list
    :param ssh: A list of all required private SSH keys.
    """
    command: str
    distro: str
    package: str

    apt: List[str] = field(default_factory=lambda: [])
    compiler: str = field(default_factory=lambda: 'catkin_make')
    entrypoint: List[str] = field(default_factory=lambda: [])
    env: List[EnvironmentVariable] = field(default_factory=lambda: [])
    hostname: List[str] = field(default_factory=lambda: [])
    rosinstall: List[str] = field(default_factory=lambda: [])
    run: List[str] = field(default_factory=lambda: [])
    ssh: List[SSHKey] = field(default_factory=lambda: [])

    def __post_init__(self) -> None:

        # Ensure no field is left undefined.
        for field_name, value in self.__dict__.items():
            if value is None:
                print(f"Field '{field_name}' was declared but left undefined.")
                sys.exit(1)

        if self.ssh and not self.rosinstall:
            print('SSH keys were provided but no .rosinstall was declared.')
            sys.exit(1)

        if self.compiler not in ['catkin_make', 'colcon']:
            print(f'Unsupported compiler "{self.compiler}".')
            sys.exit(1)
