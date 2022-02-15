from rich import print as rich_print


class MessageLogger:
    """
    A logger for text messages.
    """

    def error(self, message: str) -> None:
        """
        Log an error message.

        :type message: string
        :param message: The error message to log.
        """
        rich_print(f'[bold red]ERROR - {message}[/bold red]')

    def warning(self, message: str) -> None:
        """
        Log a warning message.

        :type message: string
        :param message: The warning message to log.
        """
        rich_print(f'[bold yellow]WARNING - {message}[/bold yellow]')

    def info(self, message: str) -> None:
        """
        Log textual information.

        :type message: string
        :param message: The message content.
        """
        rich_print(f'[bold green]{message}[/bold green]')
