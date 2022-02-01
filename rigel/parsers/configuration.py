import sys
from importlib import import_module
from rigel.files import (
    ImageConfigurationFile,
    EnvironmentVariable,
    SSHKey
)
from rigel.plugins import RegistryPlugin, SimulationPlugin
from typing import Any, Dict, List, Tuple, Union

YAMLData = Dict[str, Any]


class ConfigurationFileParser:

    dockerfile: ImageConfigurationFile = None
    registry_plugins: List[RegistryPlugin] = []
    simulation_plugins: List[SimulationPlugin] = []

    def __segment_data(self, yaml_data: YAMLData) -> Tuple[YAMLData, List[YAMLData], List[YAMLData]]:

        build_data = yaml_data.get('build')
        if build_data is None:
            print("Provided Rigelfile misses required section 'build' .")
            sys.exit(1)

        registry_plugins_data = yaml_data.get('deploy') if 'deploy' in yaml_data else []
        simulation_plugins_data = yaml_data.get('simulate') if 'simulate' in yaml_data else []

        return build_data, registry_plugins_data, simulation_plugins_data

    def __build_dockerfile(self, yaml_data: YAMLData) -> None:

        try:
            ssh = []
            if 'ssh' in yaml_data:
                for key in yaml_data['ssh']:
                    ssh.append(SSHKey(**key))
            yaml_data['ssh'] = ssh

            envs = []
            if 'env' in yaml_data:
                for env in yaml_data['env']:
                    name, value = env.strip().split('=')
                    envs.append(EnvironmentVariable(name, value))
            yaml_data['env'] = envs

            self.dockerfile = ImageConfigurationFile(**yaml_data)

        except Exception as err:
            print(err)
            exit(1)

    def __load_plugins(self, yaml_data: YAMLData, container: List[Union[RegistryPlugin, SimulationPlugin]]) -> None:
        for plugin_data in yaml_data:

            try:
                plugin_name = plugin_data.pop('plugin')
            except KeyError:
                print("Plugin was declared without required field 'plugin' .")
                exit(1)

            try:
                print(f"Loading plugin '{plugin_name}'.Plugin ")

                module = import_module(plugin_name)
                cls = getattr(module, 'Plugin')
                container.append(cls(**plugin_data))
                print(f"Using external registry plugin '{plugin_name}' .")

            except Exception as err:
                print(err)
                exit(1)

    def __init__(self, yaml_data: YAMLData) -> None:

        build_data, registry_plugins_data, simulation_plugins_data = self.__segment_data((yaml_data))
        self.__build_dockerfile(build_data)
        self.__load_plugins(registry_plugins_data, self.registry_plugins)
        self.__load_plugins(simulation_plugins_data, self.simulation_plugins)
