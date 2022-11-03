from pathlib import Path
from pydantic import BaseModel, validator
from rigel.exceptions import UnsupportedCompilerError
from rigel.loggers import get_logger
from rigel.models.package import Package, Target
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict, List
from .renderer import Renderer


LOGGER = get_logger()


class PluginModel(BaseModel):
    """A plugin that creates a ready-to-use Dockerfile for an existing ROS package.

    :type command: string
    :cvar command: The command to be executed once a container starts executing.
    :type distro: string
    :cvar distro: The target ROS distro. This field is automatically populated by Rigel.
    :type apt: List[string]
    :cvar apt: The name of dependencies to be installed using APT.
    :type compiler: string
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
    :type run: List[string]
    :cvar run: A list of commands to be executed while building the Docker image.
    :type username: string
    :cvar username: The desired username. Defaults to 'user'.
    """
    # Required fields.
    command: str
    distro: str
    package: Package

    # Optional fields.
    apt: List[str] = []
    compiler: str = 'catkin_make'

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


class Plugin(PluginBase):

    def __init__(self, distro: str, targets: List[Target]) -> None:
        super().__init__(distro, targets)

    def setup(self) -> None:
        self.__targets = [
            (package, package_data, PluginModel(distro=self.distro, package=package_data, **plugin_data))
            for package, package_data, plugin_data in self.targets]

    def run(self) -> None:

        for package, package_data, plugin_model in self.__targets:

            LOGGER.warning(f"Creating files for package '{package}'")

            Path(package_data.dir).mkdir(parents=True, exist_ok=True)

            renderer = Renderer(plugin_model)

            renderer.render('Dockerfile.j2', f'{package_data.dir}/Dockerfile')
            LOGGER.info(f"Created file {package_data.dir}/Dockerfile")

            renderer.render('entrypoint.j2', f'{package_data.dir}/entrypoint.sh')
            LOGGER.info(f"Created file {package_data.dir}/entrypoint.sh")

            if package_data.ssh:
                renderer.render('config.j2', f'{package_data.dir}/config')
                LOGGER.info(f"Created file {package_data.dir}/config")

    def stop(self) -> None:
        pass  # do nothing
