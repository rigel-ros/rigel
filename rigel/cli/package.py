# import click
# from rigel.exceptions import RigelError, UnknownROSPackagesError
# from rigel.files import RigelfileParser
# from rigel.loggers import get_logger
# from rigel.models import DockerSection
# from rigel.plugins import PluginLoader, PluginRunner
# from rigel.ros import ROSPackage
# from rigel.simulations import SimulationRequirementsParser
# from rigel.simulations.requirements import SimulationRequirementsManager
# from sys import exit
# from typing import Tuple

# LOGGER = get_logger()


# @click.group()
# def package() -> None:
#     """
#     Manage Rigel-ROS packages
#     """
#     pass


# @click.command()
# @click.option('--pkg', multiple=True, help='A list of desired packages.')
# @click.option("--load", is_flag=True, show_default=True, default=False, help="Store built image locally.")
# @click.option("--push", is_flag=True, show_default=True, default=False, help="Store built image in a remote registry.")
# def build(pkg: Tuple[str], load: bool, push: bool) -> None:
#     """
#     Build a Docker image of your ROS packages.
#     """
#     list_packages = list(pkg)
#     rigelfile = RigelfileParser().parse('./Rigelfile')
#     try:
#         if not list_packages:  # consider all declared packages
#             desired_packages = rigelfile.packages
#         else:
#             desired_packages = []
#             for package in rigelfile.packages:
#                 if package.package in list_packages:
#                     desired_packages.append(package)
#                     list_packages.remove(package.package)
#             if list_packages:  # check if an unknown package was referenced
#                 raise UnknownROSPackagesError(packages=', '.join(list_packages))

#         for package in desired_packages:
#             if isinstance(package, DockerSection):
#                 ROSPackage.containerize_package(package, load, push)
#             else:  # DockerfileSection
#                 ROSPackage.build_image(package, load, push)

#     except RigelError as err:
#         LOGGER.error(err)
#         exit(err.code)


# @click.command()
# @click.option('--pkg', multiple=True, help='A list of desired packages.')
# def create(pkg: Tuple[str]) -> None:
#     """
#     Create all files required to containerize your ROS packages.
#     """
#     list_packages = list(pkg)
#     try:
#         rigelfile = RigelfileParser().parse('./Rigelfile')
#         if not list_packages:  # consider all declared packages
#             desired_packages = rigelfile.packages
#         else:
#             desired_packages = []
#             for package in rigelfile.packages:
#                 if package.package in list_packages:
#                     desired_packages.append(package)
#                     list_packages.remove(package.package)
#             if list_packages:  # check if an unknown package was referenced
#                 raise UnknownROSPackagesError(packages=', '.join(list_packages))

#         for package in desired_packages:
#             if isinstance(package, DockerSection):
#                 ROSPackage.create_package_files(package)

#     except RigelError as err:
#         LOGGER.error(err)
#         exit(err.code)


# @click.command()
# def deploy() -> None:
#     """
#     Push a Docker image to a remote image registry.
#     """
#     LOGGER.info('Deploying containerized ROS package.')

#     rigelfile = RigelfileParser().parse('./Rigelfile')
#     if rigelfile.deploy:

#         try:

#             # Run external deployment plugins.
#             for plugin_section in rigelfile.deploy:
#                 plugin = PluginLoader().load(plugin_section, [], {})
#                 PluginRunner().run(plugin)

#         except RigelError as err:
#             LOGGER.error(err)
#             exit(err.code)

#     else:
#         LOGGER.warning('No deployment plugin declared inside Rigelfile.')


# @click.command()
# def run() -> None:
#     """
#     Start your containerized ROS application.
#     """
#     LOGGER.info('Starting containerized ROS application.')

#     rigelfile = RigelfileParser().parse('./Rigelfile')

#     if rigelfile.simulate:

#         for plugin_section in rigelfile.simulate.plugins:

#             requirements_manager = SimulationRequirementsManager(rigelfile.simulate.timeout)

#             # Parse simulation requirements.
#             requirements_parser = SimulationRequirementsParser()
#             for hpl_statement in rigelfile.simulate.introspection:
#                 requirement = requirements_parser.parse(hpl_statement)
#                 requirement.father = requirements_manager
#                 requirements_manager.children.append(requirement)

#             def introspection() -> None:
#                 while True:  # wait for test stage to finish
#                     if requirements_manager.finished:
#                         break
#                 print(requirements_manager)

#             # Run external simulation plugins.
#             plugin = PluginLoader().load(plugin_section, [requirements_manager], {})
#             PluginRunner().run(plugin, introspection)

#     else:
#         LOGGER.warning('No simulation plugin declared inside Rigelfile.')


# # Assemble 'package' command
# package.add_command(build)
# package.add_command(create)
# package.add_command(deploy)
# package.add_command(run)


# class PackageCommand:

#     @staticmethod
#     def add_command(group: click.Group) -> None:
#         """Registers CLI command 'package'.

#         :group: the top-level CLI 'rigel' command.
#         :type: click.Group
#         """
#         return group.add_command(package)
