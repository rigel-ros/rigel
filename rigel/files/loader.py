import yaml
from rigel.exceptions import (
    EmptyRigelfileError,
    RigelfileNotFoundError,
    UnformattedRigelfileError
)
from typing import Any


class YAMLDataLoader:
    """
    A class to extract the content of YAML files.
    """

    def __init__(self, filepath: str) -> None:
        """
        :type filepath: string
        :param filepath: The path for the YAML path.
        """
        self.filepath = filepath

    def load(self) -> Any:
        """
        Open a YAML file and return its contents.

        :rtype: dict
        :return: The YAML data.
        """

        try:

            with open(self.filepath, 'r') as configuration_file:
                yaml_data = yaml.safe_load(configuration_file)

            # Ensure that the file contains some data.
            if not yaml_data:
                raise EmptyRigelfileError()

            return yaml_data

        except FileNotFoundError:
            raise RigelfileNotFoundError()

        except yaml.YAMLError as err:

            # Collect the error details from the original error before
            # raising proper RigelError.
            message = []
            for arg in err.args:
                if isinstance(arg, str):
                    message.append(arg)
                else:
                    message.append(f'(line: {arg.line}, column: {arg.column})')

            raise UnformattedRigelfileError(trace=' '.join(message))
