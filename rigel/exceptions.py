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


class UndeclaredValueError(RigelError):
    """
    Raised whenever a Rigelfile is declared with undefined values.

    :type field: string
    :ivar field: The field that was left undefined.
    """
    base = "Invalid Rigelfile. Field '{field}' was declared but left undefined."
    code = 10


class InvalidValueError(RigelError):
    """
    Raised whenever an attempt to load a model with invalid data values is made.

    :type instance_type: Type
    :ivar instance_type: The model being instantiated.
    :type field: string
    :ivar field: The field whose specified value is invalid.
    """
    base = "Unable to create of instance of class '{instance_type}': invalid value for field '{field}'."
    code = 11


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


class MissingRequiredFieldError(RigelError):
    """
    Raised whenever an attempt is made to create an entity with insufficient data.

    :type field: string
    :ivar field: Name of the missing field.
    """
    base = "Required field '{field}' is missing."
    code = 14


class UndeclaredEnvironmentVariableError(RigelError):
    """
    Raised whenever an attempt is made to use the value of an undeclared environment variable.

    :type env: string
    :ivar env: The undeclared environment variable.
    """
    base = "Environment variable {env} is not declared."
    code = 15


class UndeclaredGlobalVariableError(RigelError):
    """
    Raised whenever an undeclared global variable is referenced.

    :type field: string
    :ivar field: Path for the field referencing the global varialble.
    :type var: string
    :ivar var: Global variable identifier.
    """
    base = "Field '{field}' set to have the value of undeclared global variable '{var}'."
    code = 16


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
