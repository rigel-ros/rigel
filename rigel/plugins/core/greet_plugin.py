from pydantic import BaseModel
from rigel.loggers import get_logger

LOGGER = get_logger()


class Plugin(BaseModel):
    """A test plugin for Rigel.
    """

    user: str

    def setup(self) -> None:
        pass  # do nothing

    def run(self) -> None:
        print(f'Hello {self.user}! Nice to see you using Rigel.')

    def stop(self) -> None:
        pass  # do nothing
