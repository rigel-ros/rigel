from pydantic import BaseModel
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
        print(f'Hello {self.user}')
        print('You are using:')
        print(f'-> Rigel:\t{self.distro}')
        print(f'-> ROS:\t\t{self.distro}')

    def stop(self) -> None:
        pass  # do nothing
