from pydantic import BaseModel
from rigel import __version__ as RIGEL_VERSION
from rigel.loggers import get_logger
from rigel.models.rigelfile import Package

LOGGER = get_logger()


class Plugin(BaseModel):
    """A basic plugin for Rigel that displays very basic information to the user.

    :cvar distro: The target ROS distribution. This field is automatically provided by Rigel.
    :type distro: str
    :cvar package: The target package identifier. This field is automatically provided by Rigel.
    :type package: Package
    :cvar user: The name of the user running Rigel.
    :type user: str
    """
    distro: str
    package: Package
    user: str

    def setup(self) -> None:
        pass  # do nothing

    def run(self) -> None:
        print()
        LOGGER.info(f'Hello {self.user}!')
        LOGGER.info(f"You are using Rigel {RIGEL_VERSION} to run a job on target ROS package '{self.package.name}'.")
        LOGGER.info(f'You are currently using ROS distribution {self.distro.capitalize()}.')
        print()

    def stop(self) -> None:
        pass  # do nothing
