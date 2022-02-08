import shutil
from pkg_resources import resource_filename


class RigelfileCreator:
    """
    A class that creates new Rigelfiles.
    """

    @staticmethod
    def create() -> None:
        """
        Create a new Rigelfile.
        """

        rigelfile_path = resource_filename(__name__, 'assets/Rigelfile')
        shutil.copyfile(rigelfile_path, 'Rigelfile')
