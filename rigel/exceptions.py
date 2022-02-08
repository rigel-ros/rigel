class RigelError(Exception):
    """
    The base exception class for all Rigel errors.

    :type base: string
    :var base: The error message.
    :type code: int
    :cvar code: The error code.
    """
    base = 'Undefined Rigel error.'
    code = 1

    def __init__(self, **kwargs):
        Exception.__init__(self, self.base.format(**kwargs))
        self.kwargs = kwargs


class RigelfileNotFound(RigelError):
    """
    Raised whenever a Rigelfile is required but is not found.
    """
    base = "Rigelfile was not found. Use 'rigel init' to create one."
    code = 2


class RigelfileAlreadyExistsError(RigelError):
    """
    Raised whenever an attempt is made to create a Rigelfile inside a folder
    that already contains a Rigelfile.
    """
    base = "A Rigelfile already exists. Use '--force' flag to write over existing Rigelfile."
    code = 3


class UnformattedRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an unformatted Rigelfile.

    :type trace: string
    :ivar trace: A message detailing what format error was found and where.
    """
    base = "Rigelfile is not properly formatted: {trace}."
    code = 4


class IncompleteRigelfileError(RigelError):
    """
    Raised whenever an attempt is made to use an incomplete Rigelfile.

    :type block: string
    :ivar block: The required block that is missing.
    """
    base = "Incomplete Rigelfile. Missing required block '{block}'."
    code = 5


class UndefinedValueError(RigelError):
    """
    Raised whenever a Rigelfile is declared with undefined values.

    :type path: string
    :ivar path: The value that was left undefined.
    """
    base = "Invalid Rigelfile. Field {path} was declared but left undefined."
    code = 6


class EmptyRigelfileError(RigelError):
    """
    Raised whenever an empty Rigelfile is found.
    """
    base = "Provided Rigelfile is empty."
    code = 7


class UnsupportedCompilerError(RigelError):
    """
    Raised whenever an attempt is made to use an unsupported compiler.

    :type compiler: string
    :ivar compiler: The name of the unsupported compiler.
    """
    base = "Unsupported compiler '{compiler}'."
    code = 8


class UnknownFieldError(RigelError):
    """
    Raised whenever an attempt is made to create an entity using unknown fields.

    :type field: string
    :ivar field: Name of the unknown field.
    """
    base = "Unknown field '{field}' found while parsing Rigelfile."
    code = 9


class MissingRequiredFieldError(RigelError):
    """
    Raised whenever an attempt is made to create an entity with insufficient data.

    :type field: string
    :ivar field: Name of the missing field.
    """
    base = "Required field '{field}' is missing."
    code = 10


class UndeclaredGlobalVariable(RigelError):
    """
    Raised whenever an attempt is made to use an undeclared global variable.

    :type var: string
    :ivar var: Name of the undeclared global variable.
    :type field: string
    :ivar field: Path for the field referencing the global varialble.
    """
    base = "Field '{field}' set to have the value of undeclared global variable '{var}'."
    code = 11


class PluginNotFoundError(RigelError):
    """
    Raised whenever an attempt is made to load a plugin that is not installed.

    :type plugin: string
    :ivar plugin: Name of the plugin.
    """
    base = "Unable to load plugin '{plugin}'. Not installed."
    code = 12
