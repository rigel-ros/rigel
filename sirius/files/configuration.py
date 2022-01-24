from dataclasses import dataclass, field
from typing import List
from sys import exit


@dataclass
class EnvironmentVariable:
    # Required fields
    name: str
    value: str


@dataclass
class SSHKey:
    # Required fields
    value: str
    hostname: str


@dataclass
class ConfigurationFile:

    # Required fields
    command: str
    distro: str
    package: str

    # Optional fields
    compiler: str = field(default_factory=lambda: 'catkin_make')
    env: List[EnvironmentVariable] = field(default_factory=lambda: [])
    rosinstall: List[str] = field(default_factory=lambda: [])
    ssh: List[SSHKey] = field(default_factory=lambda: [])

    def __post_init__(self) -> None:
        if self.ssh and not self.rosinstall:
            print('SSH keys were provided but no .rosinstall was declared.')
            exit(1)

        if self.compiler not in ['catkin_make', 'colcon']:
            print(f'Unsupported compiler "{self.compiler}".')
            exit(1)
