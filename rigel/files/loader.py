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

        # Extracted and adapted from:
        # https://stackoverflow.com/questions/52858143/how-to-ensure-there-are-no-null-values-in-my-yaml-file
        def __find_undefined(d: Dict[str, Any], path=[]) -> None:

            # NOTE: All field in a YAML file are either a list or a dict.
            # Standalone values will result in an UnformattedRigelfileError error.
            if isinstance(d, dict):  # entry point as YAML is a dict
                for k, v in d.items():
                    if v is None:
                        print('null value for', path + [k])
                    else:
                        __find_undefined(v, path + [k])

            elif isinstance(d, list):
                for idx, elem in enumerate(d):
                    if elem is None:
                        print('null value for', path + [idx])
                    else:
                        __find_undefined(elem, path + [idx])

        try:

            with open(filepath, 'r') as configuration_file:
                yaml_data = yaml.safe_load(configuration_file)

            # Ensure that the file contains some data.
            if not yaml_data:
                raise EmptyRigelfileError()

            # Ensure that no field was left undefined.

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
