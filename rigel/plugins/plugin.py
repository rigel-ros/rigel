from typing import Protocol, runtime_checkable


@runtime_checkable
class Plugin(Protocol):
    """
    This class specifies the interface that all plugins must comply with.
    """

    def run(self) -> None:
        """
        Use this function as an entry point for your plugin.
        """
        ...

    def stop(self) -> None:
        """
        Use this function to gracefully clean plugin resources.
        """
        ...
