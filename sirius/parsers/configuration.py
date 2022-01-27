from sirius.files import (
    ConfigurationFile,
    DockerImage,
    DockerRegistry,
    EnvironmentVariable,
    SSHKey
)
from typing import Any, Dict
from yaml import safe_load, YAMLError


class ConfigurationFileParser:

    configuration_file: ConfigurationFile

    def __init__(self, filepath: str) -> None:
        raw_data = self.__load_raw_data(filepath)
        try:

            ssh = []
            if 'ssh' in raw_data:
                for key in raw_data['ssh']:
                    ssh.append(SSHKey(**key))
            raw_data['ssh'] = ssh

            envs = []
            if 'env' in raw_data:
                for env in raw_data['env']:
                    name, value = env.strip().split('=')
                    envs.append(EnvironmentVariable(name, value))
            raw_data['env'] = envs

            raw_data['image'] = DockerImage(**raw_data['image'])
            raw_data['registry'] = DockerRegistry(**raw_data['registry'])

            self.configuration_file = ConfigurationFile(**raw_data)

        except Exception as err:
            print(err)
            exit(1)

    def __load_raw_data(self, filepath: str) -> Dict[str, Any]:

        try:
            with open(filepath, 'r') as configuration_file:
                yaml_data = safe_load(configuration_file)
            if not yaml_data:
                print('Empty YAML configuration file.')
                exit(1)
            if isinstance(yaml_data, str):
                print('Invalid YAML.')
                exit(1)
            return yaml_data
        except (FileNotFoundError, YAMLError) as err:
            print(err)
            exit(1)
