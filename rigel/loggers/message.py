from rich import print as rich_print


class MessageLogger:
    """
    A logger for text messages.
    """

    @staticmethod
    def error(message: str) -> None:
        """
        Log an error message.

        :type message: string
        :param message: The error message to log.
        """
        rich_print(f'[bold red]ERROR - {message}[/bold red]')

    @staticmethod
    def warning(message: str) -> None:
        """
        Log a warning message.

        :type message: string
        :param message: The warning message to log.
        """
        rich_print(f'[bold yellow]WARNING - {message}[/bold yellow]')

    @staticmethod
    def info(message: str) -> None:
        """
        Log textual information.

        :type message: string
        :param message: The message content.
        """
        rich_print(f'[bold green]{message}[/bold green]')
