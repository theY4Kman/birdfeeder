import io
import logging
import logging.config
from enum import Enum
from os.path import join, realpath
from typing import Any, Dict, List, Type, TypeVar

from pythonjsonlogger.jsonlogger import JsonFormatter
from ruamel.yaml import YAML

T = TypeVar("T", bound="Formatter")


class Formatter(Enum):
    """Define logging formatter in a simple way."""

    VERBOSE = "%(asctime)s - %(name)s(%(funcName)s:%(lineno)d) - %(levelname)s: %(message)s"
    JSON = "%(asctime)s %(name)s %(pathname)s %(funcName)s %(lineno)d %(levelname)s %(message)s"

    @classmethod
    def all(cls: Type[T]) -> List[str]:
        """Returns list with all defined formatter names."""
        # Looks like mypy can't correctly handle that for now
        return list(map(lambda i: i.name, cls))  # type: ignore


def configure_logging_formatter(formatter: Formatter = Formatter.JSON) -> None:
    """
    Configure formatter for all existing loggers.

    Note: it sets StreamHandler only
    """
    if formatter is Formatter.JSON:
        formatter_instance = JsonFormatter(formatter.value)
    else:
        formatter_instance = logging.Formatter(formatter.value)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter_instance)

    # We're setting a proper formatter on all existing loggers including these which created at import time
    for name in logging.getLogger().manager.loggerDict:  # type: ignore
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        # Prevent twice messages from child loggers like "aiohttp.access"
        logger.propagate = False


def read_logging_config(conf_filename: str, **kwargs: Any) -> Dict[str, Any]:
    file_path: str = realpath(join(__file__, "../../conf/%s" % (conf_filename,)))
    yaml_parser: YAML = YAML()
    with open(file_path) as fd:
        yml_source: str = fd.read()
        yml_source = yml_source.replace("$PROJECT_DIR", realpath(join(__file__, "../../")))
        for key, value in kwargs.items():
            yml_source = yml_source.replace(f"${key.upper()}", value)
        io_stream: io.StringIO = io.StringIO(yml_source)
        config: Dict = yaml_parser.load(io_stream)
    return config


def init_logging(
    conf_filename: str, load_common_config: bool = True, stdout_formatter: str = "verbose", **kwargs: Any
) -> None:
    """
    Read logging configuration from file and configure loggers.

    :param conf_filename: config filename, should be located in `conf` directory
    :param load_common_config: if True, load common_logging.yml and merge config from `conf_filename`
    :param stdout_formatter: should be one of the formatters defined inside config
    :param kwargs: any additional params, they are transformed to upper-case and used to replace $VARIABLEs in
        logging config
    :return:
    """

    logging_config = {}
    kwargs["stdout_formatter"] = stdout_formatter

    if load_common_config:
        logging_config = read_logging_config("common_logging.yml", **kwargs)

    logging_config.update(read_logging_config(conf_filename, **kwargs))
    logging.config.dictConfig(logging_config)
