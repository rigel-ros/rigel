from pydantic import BaseModel
from rigel.loggers import get_logger
from time import sleep

LOGGER = get_logger()


class Plugin(BaseModel):
    """A test plugin for Rigel.
    """

    setup_time: float = 3.0
    run_time: float = 3.0
    stop_time: float = 3.0

    def setup(self) -> None:
        LOGGER.info(f'Setup will require {self.setup_time} seconds')
        sleep(self.setup_time)

    def run(self) -> None:
        LOGGER.info(f'Doing something useful for {self.run_time} seconds')
        sleep(self.run_time)

    def stop(self) -> None:
        LOGGER.info(f'Releasing resources in {self.stop_time} seconds')
        sleep(self.stop_time)
