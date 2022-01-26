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

    # Optional fields
    file: bool = field(default_factory=lambda: False)


@dataclass
class ConfigurationFile:

    # Required fields
    command: str
    distro: str
    package: str

    # Optional fields
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
                exit(1)

        if self.ssh and not self.rosinstall:
            print('SSH keys were provided but no .rosinstall was declared.')
            exit(1)

        if self.compiler not in ['catkin_make', 'colcon']:
            print(f'Unsupported compiler "{self.compiler}".')
            exit(1)
