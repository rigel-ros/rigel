import click
import os
import signal
import sys
import time
from pathlib import Path
from rigelcore.clients import DockerClient
from rigelcore.exceptions import RigelError
from rigelcore.loggers import ErrorLogger, MessageLogger
from rigelcore.simulations import (
    SimulationRequirementsManager,
    SimulationRequirementsParser
)
from rigel.exceptions import (
    RigelfileAlreadyExistsError,
    UnknownROSPackagesError
)
from rigel.files import (
    Renderer,
    RigelfileCreator,
    YAMLDataDecoder,
    YAMLDataLoader
)
from rigel.models import DockerSection, Rigelfile, PluginSection
from rigel.plugins import Plugin, PluginInstaller
from rigelcore.models import ModelBuilder
from typing import Any, Dict, List, Tuple

from rigel.plugins.loader import PluginLoader


MESSAGE_LOGGER = MessageLogger()


def handle_rigel_error(err: RigelError) -> None:
    """
    Handler function for errors of type RigelError .
    :type err: RigelError
    :param err: The error to be handled
    """
    error_logger = ErrorLogger()
    error_logger.log(err)
    sys.exit(err.code)


def create_folder(path: str) -> None:
    """
    Create a folder in case it does not exist yet.

    :type path: string
    :param path: Path of the folder to be created.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


# TODO: change return type to Rigelfile
def parse_rigelfile() -> Any:
    """
    Parse information inside local Rigelfile.

    :rtype: rigle.models.Rigelfile
    :return: The parsed information.
    """
    loader = YAMLDataLoader('./Rigelfile')
    decoder = YAMLDataDecoder()

    yaml_data = decoder.decode(loader.load())

    builder = ModelBuilder(Rigelfile)
    return builder.build([], yaml_data)


def rigelfile_exists() -> bool:
    """
    Verify if a Rigelfile is present.

    :rtype: bool
    :return: True if a Rigelfile is found at the current directory. False otherwise.
    """
    return os.path.isfile('./Rigelfile')


def load_plugin(
        plugin: PluginSection,
        application_args: List[Any],
        application_kwargs: Dict[str, Any]
        ) -> Tuple[str, Plugin]:
    """
    Load an external plugin.

    :type plugin: rigel.models.PluginSection
    :param plugin: Metadata about the external plugin.
    :type application_args: List[Any]
    :param application_args: Additional positional arguments to be passed the plugin.
    :type application_kwargs: Dict[str, Any]
    :param application_kwargs: Additional keyword arguments to be passed the plugin.

    :rtype: Tuple[str, rigel.plugin.Plugin]
    :return: An instance of the external plugin.
    """
    MESSAGE_LOGGER.warning(f"Loading external plugin '{plugin.name}'.")
    try:

        loader = PluginLoader()

        if application_args:
            plugin.args = application_args + plugin.args

        if application_kwargs:
            plugin.kwargs.update(application_kwargs)

        plugin_instance = loader.load(plugin)

    except RigelError as err:
        handle_rigel_error(err)

    return (plugin.name, plugin_instance)


def run_plugin(plugin: Tuple[str, Plugin]) -> None:
    """
    Run an external plugin.

    :type plugin: Tuple[str, rigel.plugin.Plugin]
    :param plugin: An external plugin to be run.
    """
    try:

        plugin_name, plugin_instance = plugin

        def stop_plugin(*args: Any) -> None:
            plugin_instance.stop()
            MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' stopped executing gracefully.")
            sys.exit(0)

        signal.signal(signal.SIGINT, stop_plugin)
        signal.signal(signal.SIGTSTP, stop_plugin)

        MESSAGE_LOGGER.warning(f"Executing external plugin '{plugin_name}'.")
        plugin_instance.run()

        plugin_instance.stop()
        MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' finished execution with success.")

    except RigelError as err:
        handle_rigel_error(err)


def run_simulation_plugin(
    plugin: Tuple[str, Plugin],
    manager: SimulationRequirementsManager,
    timeout: int
) -> None:
    """
    Run an external simulation plugin.

    :type plugin: Tuple[str, rigel.plugin.Plugin]
    :param plugin: An external plugin to be run.
    :type manager: rigelcore.simulations.SimulationRequirementsManager
    :param manager: The simulation requirements associated with the external plugin.
    :type manager: rigelcore.simulations.SimulationRequirementsManager
    :param manager: The simulation requirements associated with the external plugin.
    :type timeout: int
    :param timeout: The simulation timeout in seconds.
    """
    try:

        plugin_name, plugin_instance = plugin

        def stop_plugin(*args: Any) -> None:
            plugin_instance.stop()
            MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' stopped executing gracefully.")
            sys.exit(0)

        signal.signal(signal.SIGINT, stop_plugin)
        signal.signal(signal.SIGTSTP, stop_plugin)

        MESSAGE_LOGGER.warning(f"Executing external plugin '{plugin_name}'.")
        plugin_instance.run()
        MESSAGE_LOGGER.warning("Simulation started.")

        initial_time = time.time()
        while True:  # implement timeout mechanism
            passed_time = time.time() - initial_time
            if passed_time > timeout:
                MESSAGE_LOGGER.error(f"Timeout ({passed_time}s). Simulation requirements were not satisfied on time.")
                break
            elif manager.requirements_satisfied:
                MESSAGE_LOGGER.info(f"All simulation requirements were satisfied on {passed_time}s.")
                break

        plugin_instance.stop()
        MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' finished executing.")

    except RigelError as err:
        handle_rigel_error(err)


@click.group()
def cli() -> None:
    """
    Rigel - containerize and deploy your ROS application using Docker
    """
    pass


@click.command()
@click.option('--force', is_flag=True, default=False, help='Write over an existing Rigelfile.')
def init(force: bool) -> None:
    """
    Create an empty Rigelfile.
    """
    try:

        if rigelfile_exists() and not force:
            raise RigelfileAlreadyExistsError()

        rigelfile_creator = RigelfileCreator()
        rigelfile_creator.create()
        MESSAGE_LOGGER.info('Rigelfile created with success.')

    except RigelError as err:
        handle_rigel_error(err)


def create_package_files(package: DockerSection) -> None:
    """
    Create all the files required to containerize a given ROS package.

    :type package: rigel.models.DockerSection
    :param package: The ROS package whose Dockerfile is to be created.
    """
    MESSAGE_LOGGER.warning(f"Creating build files for package {package.package}.")

    if package.dir:
        path = os.path.abspath(f'{package.dir}/{package.package}/.rigel_config')
    else:
        path = os.path.abspath(f'.rigel_config/{package.package}')

    create_folder(path)

    renderer = Renderer(package)

    renderer.render('Dockerfile.j2', f'{path}/Dockerfile')
    MESSAGE_LOGGER.info(f"Created file {path}/Dockerfile")

    renderer.render('entrypoint.j2', f'{path}/entrypoint.sh')
    MESSAGE_LOGGER.info(f"Created file {path}/entrypoint.sh")

    if package.ssh:
        renderer.render('config.j2', f'{path}/config')
        MESSAGE_LOGGER.info(f"Created file {path}/config")


@click.command()
@click.option('--pkg', multiple=True, help='A list of desired packages.')
def create(pkg: Tuple[str]) -> None:
    """
    Create all files required to containerize your ROS packages.
    """
    list_packages = list(pkg)
    try:
        rigelfile = parse_rigelfile()
        if not list_packages:  # consider all declared packages
            desired_packages = rigelfile.packages
        else:
            desired_packages = []
            for package in rigelfile.packages:
                if package.package in list_packages:
                    desired_packages.append(package)
                    list_packages.remove(package.package)
            if list_packages:  # check if an unknown package was referenced
                raise UnknownROSPackagesError(packages=', '.join(list_packages))

        for package in desired_packages:
            create_package_files(package)

    except RigelError as err:
        handle_rigel_error(err)


def containerize_package(package: DockerSection) -> None:
    """
    Containerize a given ROS package.

    :type package: rigel.models.DockerSection
    :param package: The ROS package whose Dockerfile is to be created.
    """
    MESSAGE_LOGGER.warning(f"Containerizing package {package.package}.")

    if package.ssh and not package.rosinstall:
        MESSAGE_LOGGER.warning('No .rosinstall file was declared. Recommended to remove unused SSH keys from Dockerfile.')

    buildargs: Dict[str, str] = {}
    for key in package.ssh:
        if not key.file:
            value = os.environ[key.value]  # NOTE: SSHKey model ensures that environment variable is declared.
            buildargs[key.value] = value

    if package.dir:
        path = os.path.abspath(package.dir)
    else:
        path = os.path.abspath(f'.rigel_config/{package.package}')

    MESSAGE_LOGGER.info(f"Building Docker image '{package.image}'.")
    builder = DockerClient()
    builder.build_image(path, '.rigel_config/Dockerfile', package.image, buildargs)
    MESSAGE_LOGGER.info(f"Docker image '{package.image}' built with success.")


@click.command()
@click.option('--pkg', multiple=True, help='A list of desired packages.')
def build(pkg: Tuple[str]) -> None:
    """
    Build a Docker image of your ROS packages.

    :type package: rigel.models.DockerSection
    :param package: The ROS package to be containerized.
    """
    list_packages = list(pkg)
    rigelfile = parse_rigelfile()
    try:
        if not list_packages:  # consider all declared packages
            desired_packages = rigelfile.packages
        else:
            desired_packages = []
            for package in rigelfile.packages:
                if package.package in list_packages:
                    desired_packages.append(package)
                    list_packages.remove(package.package)
            if list_packages:  # check if an unknown package was referenced
                raise UnknownROSPackagesError(packages=', '.join(list_packages))

        for package in desired_packages:
            containerize_package(package)

    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def deploy() -> None:
    """
    Push a Docker image to a remote image registry.
    """
    MESSAGE_LOGGER.info('Deploying containerized ROS package.')

    rigelfile = parse_rigelfile()
    if rigelfile.deploy:

        # Run external deployment plugins.
        for plugin_section in rigelfile.deploy:
            plugin = load_plugin(plugin_section, [], {})
            run_plugin(plugin)

    else:
        MESSAGE_LOGGER.warning('No deployment plugin declared inside Rigelfile.')


@click.command()
def run() -> None:
    """
    Start your containerized ROS application.
    """
    MESSAGE_LOGGER.info('Starting containerized ROS application.')

    rigelfile = parse_rigelfile()
    if rigelfile.simulate:

        for plugin_section in rigelfile.simulate.plugins:

            requirements_manager = SimulationRequirementsManager()

            # Parse simulation requirements.
            requirements_parser = SimulationRequirementsParser()
            for hpl_statement in rigelfile.simulate.introspection:
                requirements = requirements_parser.parse(hpl_statement)
                for requirement in requirements:
                    requirements_manager.add_simulation_requirement(requirement)

            # Run external simulation plugins.
            plugin = load_plugin(plugin_section, [requirements_manager], {})
            run_simulation_plugin(plugin, requirements_manager, rigelfile.simulate.timeout)

    else:
        MESSAGE_LOGGER.warning('No simulation plugin declared inside Rigelfile.')


@click.command()
@click.argument('plugin', type=str)
@click.option('--host', default='github.com', help="URL of the hosting platform. Default is 'github.com'.")
@click.option('--ssh', is_flag=True, default=False, help='Whether the plugin is public or private. Use flag when private.')
def install(plugin: str, host: str, ssh: bool) -> None:
    """
    Install external plugins.
    """
    try:
        installer = PluginInstaller(plugin, host, ssh)
        installer.install()
    except RigelError as err:
        handle_rigel_error(err)


# Add commands to CLI
cli.add_command(init)
cli.add_command(build)
cli.add_command(create)
cli.add_command(deploy)
cli.add_command(install)
cli.add_command(run)


def main() -> None:
    """
    Rigel application entry point.
    """
    cli()


if __name__ == '__main__':
    main()
