import logging

BLUE = "\x1b[34;1m"
GREEN = "\x1b[32;1m"
RED = "\x1b[31;1m"
YELLOW = "\x1b[33;1m"
RESET = "\x1b[0m"


# Class extracted and adapted on Sergey Pleshakov's answer at:
# https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
class RigelFormatter(logging.Formatter):
    """A logger formatter to be used by all Rigel classes."""

    formats = {
        logging.DEBUG: f"{GREEN}%(message)s{RESET}",
        logging.INFO: f"{BLUE}%(message)s{RESET}",
        logging.WARNING: f"{YELLOW}%(levelname)s - %(message)s{RESET}",
        logging.ERROR: f"{RED}%(levelname)s - %(message)s{RESET}",
        logging.CRITICAL: f"{RED}%(levelname)s - %(message)s{RESET}"
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger() -> logging.Logger:
    """Retrieve a message logger.

    :return: the message logger
    :rtype: logging.Logger
    """
    logger = logging.getLogger("Rigel")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(RigelFormatter())
        logger.addHandler(ch)

    return logger
