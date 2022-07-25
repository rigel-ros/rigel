from rigelcore.exceptions import RigelError


class RigelfileNotFoundError(RigelError):
    """
    Raised whenever a Rigelfile is required but is not found.
    """
    base = "Rigelfile was not found. Use 'rigel init' to create one."
    code = 6


class RigelfileAlreadyExistsError(RigelError):
    """
    Raised whenever an attempt is made to create a Rigelfile inside a folder
    that already contains a Rigelfile.
    """
    base = "A Rigelfile already exists. Use '--force' flag to write over existing Rigelfile."
    code = 7


class UnformattedRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an unformatted Rigelfile.

    :type trace: string
    :ivar trace: A message detailing what format error was found and where.
    """
    base = "Rigelfile is not properly formatted: {trace}."
    code = 8


class IncompleteRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an incomplete Rigelfile.

    :type block: string
    :ivar block: The required block that is missing.
    """
    base = "Incomplete Rigelfile. Missing required block '{block}'."
    code = 9


class EmptyRigelfileError(RigelError):
    """
    Raised whenever an empty Rigelfile is found.
    """
    base = "Provided Rigelfile is empty."
    code = 12


class UnsupportedCompilerError(RigelError):
    """
    Raised whenever an attempt is made to use an unsupported compiler.

    :type compiler: string
    :ivar compiler: The name of the unsupported compiler.
    """
    base = "Unsupported compiler '{compiler}'."
    code = 13


class UnsupportedPlatformError(RigelError):
    """
    Raised whenever an attempt is build an image for an unsupported platform.

    :type compiler: platform
    :ivar compiler: The unsupported platform.
    """
    base = "Unsupported platform '{platform}'."
    code = 14


class InvalidPlatformError(RigelError):
    """
    Raised whenever an attemp to use an invalid platform is made.

    :param RigelError: platform
    :type RigelError: The invalid platform.
    """
    base = "An invalid platform was used: '{platform}'."
    code = 15


class PluginNotFoundError(RigelError):
    """
    Raised whenever an attempt is made to load a plugin that is not installed.

    :type plugin: string
    :ivar plugin: Name of the plugin.
    """
    base = ("Unable to load plugin '{plugin}'. Make sure plugin is installed in your system.\n"
            "For more information on external plugin installation run command 'rigel install --help'.")
    code = 17


class PluginInstallationError(RigelError):
    """
    Raised whenever an error occurs while installing an external plugin.

    :type plugin: string
    :ivar plugin: Name of the plugin to be installed.
    """
    base = "An error occurred while installing external plugin {plugin}."
    code = 18


class PluginNotCompliantError(RigelError):
    """
    Raised whenever an external plugin is loaded that is not compliant with
    the rigel.plugins.Protocol class.

    :type plugin: string
    :ivar plugin: Name of the plugin
    :type cause: string
    :ivar cause: Reason why external plugin is not compliant.
    """
    base = "Plugin '{plugin}' does not comply with Rigel plugin protocol: {cause}"
    code = 19


class InvalidPluginNameError(RigelError):
    """
    Raised whenever an invalid plugin name is passed.

    :type plugin: string
    :ivar plugin: The invalid plugin name.
    """
    base = "Invalid plugin name '{plugin}'."
    code = 20


class UnknownROSPackagesError(RigelError):
    """
    Raised whenever unlisted ROS package are referenced.

    :type packages: List[string]
    :ivar packages: List of unknown ROS packages.
    """
    base = "The following packages were not declared in the Rigelfile: {packages}."
    code = 21
