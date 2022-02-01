import sys
from importlib import import_module
from rigel.files import (
    ImageConfigurationFile,
    EnvironmentVariable,
    SSHKey
)
from rigel.exceptions import IncompleteRigelfileError
from rigel.plugins import RegistryPlugin, SimulationPlugin
from typing import Any, Dict, List, Tuple, Union

YAMLData = Dict[str, Any]


class RigelfileParser:
    """
    A parser of Rigelfiles.

    :type dockerfile: rigel.files.ImageConfigurationFile
    :cvar dockerfile: Information regarding how to containerize the ROS application.
    :type registry_plugins: List[rigel.files.RegistryPlugin]
    :cvar registry_plugins: List of plugins to be used to deploy the containerized ROS application.
    :type simulation_plugins: List[rigel.files.SimulationPlugin]
    :cvar simulation_plugins: List of plugins to be used to run the containerized ROS application.
    """

    dockerfile: ImageConfigurationFile
    registry_plugins: List[RegistryPlugin]
    simulation_plugins: List[SimulationPlugin]

    def __segment_data(self, yaml_data: YAMLData) -> Tuple[YAMLData, List[YAMLData], List[YAMLData]]:
        """
        Segment the data within a Rigelfile into its constituient logic blocks.

        Each Rigelfile contains YAML data that can be broken into three main logic blocks:
        - 'build': holds all data concerning how to containerize the ROS application.
        - 'deploy': holds all data concerning how and where to deploy the containerized ROS application.
        - 'simulate': holds all data concerning how to start executing the containerized ROS application.   

        :type yaml_data: Dict[str, Any]
        :param yaml_data: All the data extracted from a Rigelfile.

        :rtype: Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]
        :return: A tuple containing the segmented data and separated according to logic block.
        """
        # The 'build' block is mandatory and its existence must be checked.
        build_data = yaml_data.get('build')
        if build_data is None:
            raise IncompleteRigelfileError(block='build')

        # The 'deploy' and 'simulate' blocks are not mandatory.
        registry_plugins_data = yaml_data.get('deploy') if 'deploy' in yaml_data else []
        simulation_plugins_data = yaml_data.get('simulate') if 'simulate' in yaml_data else []

        return build_data, registry_plugins_data, simulation_plugins_data

    def __build_dockerfile(self, yaml_data: YAMLData) -> ImageConfigurationFile:
        """
        Parse the data contained within the logical block 'build'.

        :type yaml_data: Dict[str, Any]
        :param yaml_data: All data concerning how to containertize the ROS application.

        :rtype: rigel.files.ImageConfigurationFile
        :return: A data aggregator.  
        """
        try:

            ssh = []
            if 'ssh' in yaml_data:
                for key in yaml_data['ssh']:
                    ssh.append(SSHKey(**key))
            yaml_data['ssh'] = ssh

        except Exception as err:
            print(err.args)

            if 'got an unexpected keyword' in err.args[0]:
                print('raise UnknownFieldError(type, field_name)')
            elif 'missing' in err.args[0]:
                print('raise MissingRequiredFieldError(type, field_name)')

            exit(1)

        try:

            envs = []
            if 'env' in yaml_data:
                for env in yaml_data['env']:
                    name, value = env.strip().split('=')
                    envs.append(EnvironmentVariable(name, value))
            yaml_data['env'] = envs

        except Exception as err:
            print(err)
            exit(1)

        self.dockerfile = ImageConfigurationFile(**yaml_data)


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
