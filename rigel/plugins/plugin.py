import signal
from rigel.loggers import get_logger
from rigel.models.package import Target
from typing import Any, List

LOGGER = get_logger()


class Plugin:
    """This class specifies the interface that all plugins must comply with.
    """

    def __init__(self, distro: str, targets: List[Target]) -> None:
        self.distro = distro
        self.targets = targets

    def __enter__(self) -> Any:
        signal.signal(signal.SIGINT, self.stop_plugin)
        signal.signal(signal.SIGTSTP, self.stop_plugin)
        self.setup()
        return self

    def __str__(self) -> str:
        return f'DISTRO: {self.distro}\nTARGETS: {self.targets}'

    def stop_plugin(*args: Any) -> None:
        exit(1)  # this will trigger __exit__

    def __exit__(
        self,
        exc_type: Any,  # ideally -> type[BaseException]
        exc_val: Any,  # ideally -> Optional[BaseException]
        exc_tb: Any  # ideally -> Optional[TracebackType]
    ) -> None:
        self.stop()

    def setup(self) -> None:
        """Use this function to allocate plugin resoures.
        """
        pass

    def run(self) -> None:
        """Use this function as an entry point for your plugin.
        """
        pass

    def stop(self) -> None:
        """Use this function to gracefully clean plugin resources.
        """
        pass
