import click
import os
import signal
import sys
from pathlib import Path
from rigelcore.clients import DockerClient
from rigelcore.exceptions import RigelError
from rigelcore.loggers import ErrorLogger, MessageLogger
from rigelcore.simulations import SimulationRequirementsParser
from rigelcore.simulations.requirements import SimulationRequirementsManager
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
from rigel.models.docker import SUPPORTED_PLATFORMS, DockerfileSection
from rigel.plugins import Plugin, PluginInstaller
from rigel.plugins.loader import PluginLoader
from rigelcore.models import ModelBuilder
from typing import Any, Dict, List, Tuple, Union


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
) -> None:
    """
    Run an external simulation plugin.

    :type plugin: Tuple[str, rigel.plugin.Plugin]
    :param plugin: An external plugin to be run.
    :type manager: rigelcore.simulations.SimulationRequirementsManager
    :param manager: The simulation requirements associated with the external plugin.
    :type manager: rigelcore.simulations.SimulationRequirementsManager
    :param manager: The simulation requirements associated with the external plugin.
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

        while True:  # wait for test stage to finish
            if manager.finished:
                break

        print(manager)
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
        path = os.path.abspath(f'{package.dir}/.rigel_config')
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
            if isinstance(package, DockerSection):
                create_package_files(package)

    except RigelError as err:
        handle_rigel_error(err)


def login_registry(package: Union[DockerSection, DockerfileSection]) -> None:
    """
    Login to a Docker image registry.

    :param package: The ROS package to be containerized and deployed.
    :type package: DockerSection
    """
    docker = DockerClient()

    # Authenticate with registry
    if package.registry:

        server = package.registry.server
        username = package.registry.username
        password = package.registry.password

        try:

            MESSAGE_LOGGER.info(f'Authenticating with registry {server}')
            docker.login(
                server,
                username,
                password
            )

        except RigelError as err:
            handle_rigel_error(err)


def generate_paths(package: DockerSection) -> Tuple[str, str]:
    if package.dir:
        return (
            os.path.abspath(f'{package.dir}'),                      # package root
            os.path.abspath(f'{package.dir}/.rigel_config')         # Dockerfile folder
        )
    else:
        return (
            os.path.abspath(f'.rigel_config/{package.package}'),    # package root
            os.path.abspath(f'.rigel_config/{package.package}')     # Dockerfile folder
        )


def containerize_package(package: DockerSection, load: bool, push: bool) -> None:
    """
    Containerize a given ROS package.

    :type package: rigel.models.DockerSection
    :param package: The ROS package whose Dockerfile is to be created.
    :type load: bool
    :param package: Store built image locally.
    :type push: bool
    :param package: Store built image in a remote registry.
    """
    MESSAGE_LOGGER.warning(f"Containerizing package {package.package}.")
    if package.ssh and not package.rosinstall:
        MESSAGE_LOGGER.warning('No .rosinstall file was declared. Recommended to remove unused SSH keys from Dockerfile.')

    buildargs: Dict[str, str] = {}
    for key in package.ssh:
        if not key.file:
            value = os.environ[key.value]  # NOTE: SSHKey model ensures that environment variable is declared.
            buildargs[key.value] = value

    path = generate_paths(package)

    docker = DockerClient()

    login_registry(package)

    platforms = package.platforms or None

    docker.create_builder('rigel-builder', use=True)
    MESSAGE_LOGGER.info("Created builder 'rigel-builder'")

    # Ensure that QEMU is properly configured before building an image.
    for docker_platform, _, qemu_config_file in SUPPORTED_PLATFORMS:
        if not os.path.exists(f'/proc/sys/fs/binfmt_misc/{qemu_config_file}'):
            docker.run_container(
                'qus',
                'aptman/qus',
                command=['-s -- -c -p'],
                privileged=True,
                remove=True,
            )
            MESSAGE_LOGGER.info(f"Created QEMU configuration file for '{docker_platform}'")

    # Build the Docker image.
    MESSAGE_LOGGER.info(f"Building Docker image '{package.image}'")
    try:

        kwargs = {
            "file": f'{path[1]}/Dockerfile',
            "tags": package.image,
            "load": load,
            "push": push
        }

        if buildargs:
            kwargs["build_args"] = buildargs

        if platforms:
            kwargs["platforms"] = platforms

        docker.build_image(path[0], **kwargs)

        MESSAGE_LOGGER.info(f"Docker image '{package.image}' built with success.")
        if push:
            MESSAGE_LOGGER.info(f"Docker image '{package.image}' pushed with success.")

    except RigelError as err:
        handle_rigel_error(err)

    finally:
        # In all situations make sure to remove the builder if existent
        docker.remove_builder('rigel-builder')
        MESSAGE_LOGGER.info("Removed builder 'rigel-builder'")


def build_image(package: DockerfileSection, load: bool, push: bool) -> None:
    """
    Containerize a given ROS package (existing Dockerfile).

    :type package: rigel.models.DockerfileSection
    :param package: The Dockerfile to use to containerize.
    :type load: bool
    :param package: Store built image locally.
    :type push: bool
    :param package: Store built image in a remote registry.
    """
    MESSAGE_LOGGER.warning(f"Creating Docker image using provided Dockerfile at {package.dockerfile}")

    login_registry(package)

    path = os.path.abspath(package.dockerfile)

    MESSAGE_LOGGER.info(f"Building Docker image {package.image}")
    builder = DockerClient()
    kwargs = {
        "tags": package.image,
        "load": load,
        "push": push
    }
    builder.build_image(path, **kwargs)

    MESSAGE_LOGGER.info(f"Docker image '{package.image}' built with success.")


@click.command()
@click.option('--pkg', multiple=True, help='A list of desired packages.')
@click.option("--load", is_flag=True, show_default=True, default=False, help="Store built image locally.")
@click.option("--push", is_flag=True, show_default=True, default=False, help="Store built image in a remote registry.")
def build(pkg: Tuple[str], load: bool, push: bool) -> None:
    """
    Build a Docker image of your ROS packages.
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
            if isinstance(package, DockerSection):
                containerize_package(package, load, push)
            else:  # DockerfileSection
                build_image(package, load, push)

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

            requirements_manager = SimulationRequirementsManager(rigelfile.simulate.timeout)

            # Parse simulation requirements.
            requirements_parser = SimulationRequirementsParser()
            for hpl_statement in rigelfile.simulate.introspection:
                requirement = requirements_parser.parse(hpl_statement)
                requirement.father = requirements_manager
                requirements_manager.children.append(requirement)

            # Run external simulation plugins.
            plugin = load_plugin(plugin_section, [requirements_manager], {})
            run_simulation_plugin(plugin, requirements_manager)

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
