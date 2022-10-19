from pydantic import BaseModel
from rigel import __version__ as RIGEL_VERSION
from rigel.loggers import get_logger

LOGGER = get_logger()


class Plugin(BaseModel):
    """A basic plugin for Rigel that displays very basic information to the user.

    :cvar distro: The ROS distribution.
    :type distro: str
    :cvar user: The name of the user running Rigel.
    :type user: str
    """

    distro: str
    user: str

    def setup(self) -> None:
        pass  # do nothing

    def run(self) -> None:
        LOGGER.info(f'Hello {self.user}! You are using:')
        LOGGER.info(f'-> Rigel:\t{RIGEL_VERSION}')
        LOGGER.info(f'-> ROS:\t\t{self.distro}')

    def stop(self) -> None:
        pass  # do nothing
