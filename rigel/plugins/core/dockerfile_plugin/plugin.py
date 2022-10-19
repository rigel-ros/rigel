import os
from pathlib import Path
from pydantic import BaseModel, validator
from rigel.exceptions import UnsupportedCompilerError
from rigel.loggers import get_logger
from rigel.files import Renderer
from typing import Any, Dict, List
from ..models import SSHKey

LOGGER = get_logger()


class Plugin(BaseModel):
    """A plugin that creates a ready-to-use Dockerfile for an existing ROS package.

    :type command: string
    :cvar command: The command to be executed once a container starts executing.
    :type distro: string
    :cvar distro: The target ROS distro. This field is automatically populated by Rigel.
    :type apt: List[string]
    :cvar apt: The name of dependencies to be installed using APT.
    :type compiler: string
    :cvar compiler: The tool with which to compile the containerized ROS workspace. Default value is 'catkin_make'.
    :type dir: string
    :cvar dir: The folder containing the ROS package source code, if required.
    :type entrypoint: List[string]
    :cvar entrypoint: A list of commands to be run while executing the entrypoint script.
    :type env: List[Dict[str, Any]]
    :cvar env: A list of environment variables to be set inside the Docker image.
    :type package: str
    :cvar package: The target package identifier. This field is automatically populated by Rigel.
    :type rosinstall: List[string]
    :cvar rosinstall: A list of all required .rosinstall files.
    :type ros_image: string
    :cvar ros_image: The official ROS Docker image to use as a base for the new Docker image.
    :type run: List[string]
    :cvar run: A list of commands to be executed while building the Docker image.
    :type ssh: List[rigel.files.SSHKey]
    :cvar ssh: A list of all required private SSH keys.
    :type username: string
    :cvar username: The desired username. Defaults to 'user'.
    """
    # Automatically provided fields.
    distro: str
    package: str

    # Required fields.
    command: str

    # Optional fields.
    apt: List[str] = []
    compiler: str = 'catkin_make'
    dir: str = ''
    entrypoint: List[str] = []
    env: List[Dict[str, Any]] = []
    rosinstall: List[str] = []
    ros_image: str
    run: List[str] = []
    ssh: List[SSHKey] = []
    username: str = 'rigeluser'

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        if not kwargs.get('ros_image') and kwargs.get('distro'):
            kwargs['ros_image'] = kwargs['distro']

        super().__init__(*args, **kwargs)

    @validator('compiler')
    def validate_compiler(cls, compiler: str) -> str:
        """Ensure that the specified ROS package compiler used is supported by Rigel.

        :type compiler: string
        :param compiler: ROS package compiler.
        """
        # NOTE: At the moment only "catkin" and "colcon" are supported.
        if compiler not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(compiler=compiler)
        return compiler

    def setup(self) -> None:
        pass

    def run(self) -> None:
        """Create all the files required to containerize a given ROS package.

        :type package: rigel.models.DockerSection
        :param package: The ROS package whose Dockerfile is to be created.
        """
        LOGGER.warning(f"Creating build files for package {self.package}.")

        if self.dir:
            path = os.path.abspath(f'{self.dir}/.rigel_config')
        else:
            path = os.path.abspath(f'.rigel_config/{self.package}')

        Path(path).mkdir(parents=True, exist_ok=True)

        renderer = Renderer(self)

        renderer.render('Dockerfile.j2', f'{path}/Dockerfile')
        LOGGER.info(f"Created file {path}/Dockerfile")

        renderer.render('entrypoint.j2', f'{path}/entrypoint.sh')
        LOGGER.info(f"Created file {path}/entrypoint.sh")

        if self.ssh:
            renderer.render('config.j2', f'{path}/config')
            LOGGER.info(f"Created file {path}/config")

    def stop(self) -> None:
        pass
