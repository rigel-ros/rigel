import yaml
from rigel.exceptions import (
    EmptyRigelfileError,
    RigelfileNotFound,
    UnformattedRigelfileError
)
from typing import Any, Dict

YAMLData = Dict[str, Any]


class YAMLDataLoader:
    """
    A class to extract the content of YAML files.
    """

    @staticmethod
    def load_data(filepath: str) -> YAMLData:
        """
        Open a YAML file and return its contents.

        :type filepath: string
        :param filepath: The path for the YAML path.

        :rtype: dict
        :return: The YAML data.
        """
        try:

            with open(filepath, 'r') as configuration_file:
                yaml_data = yaml.safe_load(configuration_file)

            # Ensure that the file contains some data.
            if not yaml_data:
                raise EmptyRigelfileError()

            return yaml_data

        except FileNotFoundError:
            raise RigelfileNotFound()

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
