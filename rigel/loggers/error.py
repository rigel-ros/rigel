from rich import print as rich_print
from rigel.exceptions import RigelError


class ErrorLogger:

    @staticmethod
    def log(err: RigelError) -> None:
        """
        Display error message.

        :type err: rigel.exceptions.RigelError
        :param err: The error.
        """
        rich_print(f'[red bold]{err}[/red bold] ([bold]Error: {err.code}[/ bold])')
