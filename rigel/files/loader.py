import yaml
from rigel.exceptions import (
    EmptyRigelfileError,
    RigelfileNotFound,
    UndefinedValueError,
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
        def __find_undefined(yaml_data: Dict[str, Any], path='') -> None:
            """
            Auxiliary function that recursively looks for undeclared YAML fields.

            :type yaml_data: Dict[str, Any]
            :param yaml_data: The YAML data to be analyzed.
            """

            # NOTE: All fields within a YAML file are either a list or a dict.
            # Standalone values will result in an UnformattedRigelfileError error.
            if isinstance(yaml_data, dict):  # entry point as YAML is a dict
                for k, v in yaml_data.items():
                    new_path = f'{path}.{k}'
                    if v is None:
                        raise UndefinedValueError(path=new_path)
                    else:
                        __find_undefined(v, new_path)

            elif isinstance(yaml_data, list):
                for idx, elem in enumerate(yaml_data):
                    new_path = f'{path}[{idx}]'
                    if elem is None:
                        raise UndefinedValueError(path=new_path)
                    else:
                        __find_undefined(elem, new_path)

        try:

            with open(filepath, 'r') as configuration_file:
                yaml_data = yaml.safe_load(configuration_file)

            # Ensure that the file contains some data.
            if not yaml_data:
                raise EmptyRigelfileError()

            # Ensure that no field was left undefined.
            # __find_undefined(yaml_data)

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
