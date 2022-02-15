from rich import print as rich_print
from rigel.exceptions import RigelError


class ErrorLogger:
    """
    A class that proides a common interface to display error messages.
    """

    def log(self, err: RigelError) -> None:
        """
        Display error message.

        :type err: rigel.exceptions.RigelError
        :param err: The error.
        """
        rich_print(f'[red bold]{err}[/red bold] ([bold]Error: {err.code}[/ bold])')
