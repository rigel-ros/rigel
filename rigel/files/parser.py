from typing import Any
from rigel.files import (
    YAMLDataDecoder,
    YAMLDataLoader
)
from rigel.models import Rigelfile
from rigelcore.models import ModelBuilder


class RigelfileParser:
    """
    A class to parse new Rigelfiles.
    """

    # TODO: change return type to Rigelfile
    def parse(self, path: str) -> Any:
        """
        Parse the contents of a Rigelfile.

        :path: path to Rigelfile.
        :type: str
        :rtype: rigle.models.Rigelfile
        :return: The parsed information.
        """

        loader = YAMLDataLoader(path)
        decoder = YAMLDataDecoder()

        yaml_data = decoder.decode(loader.load())

        builder = ModelBuilder(Rigelfile)
        return builder.build([], yaml_data)
