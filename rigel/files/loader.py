import sys
import yaml
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
                print('Empty YAML configuration file.')
                sys.exit(1)

            # Ensure that the data is of intended type.
            if not isinstance(yaml_data, dict):
                print('Invalid YAML.')
                sys.exit(1)

            return yaml_data

        except (FileNotFoundError, yaml.YAMLError) as err:
            print(err)
            exit(1)
