#! /usr/bin/env python3

"""
# Framework Module

This is an interim subset of functionality that will
be refactored to the new application framework when
it is ready. Nothing in this module should be specific
to Unreal Engine or to UETools.

The application code should, to the extent possible, rely
on AppContext rather than directly interacting with other
entities from this module.

See the [main README](../README.md) for more information.
"""

from typing import Optional, Annotated, Any
from types import SimpleNamespace
from pathlib import Path
from collections import ChainMap
from contextlib import contextmanager
from itertools import chain
from ruamel.yaml import YAML
import yamlpath
from yamlpath.wrappers import ConsolePrinter
from yamlpath.common import Parsers
from yamlpath import Processor
from yamlpath import YAMLPath
import logging
import os

class YAMLChainMap(ChainMap):
    """
    ChainMap variant where the dictionary is replaced by a YAML path tree.
    Queries can use either the dotted or the slash notation for segments.
    """

    logging_args = SimpleNamespace(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    def __init__(self, *maps):
        super().__init__(*maps)
        self.yaml = Parsers.get_yaml_editor()
        self.log = ConsolePrinter(YAMLChainMap.logging_args)
        self.yaml_data = None
        self.yaml_processor = None

    def load(self, source: str|Path, required: bool=True) -> bool:
        if not self.yaml:
            raise RuntimeError("YAML parser not initialized")
        if isinstance(source, str):
            source = Path(source)
        if not source.is_file():
            if required:
                raise FileNotFoundError(f"YAML file not found: {source}")
            return False
        self.yaml_data, loaded = Parsers.get_yaml_data(self.yaml, self.log, str(source))
        if not loaded:
            if required:
                raise RuntimeError(f"Failed to load YAML file: {source}")
            else:
                self.yaml_data = None
            return False
        self.yaml_processor = Processor(self.log, self.yaml_data)
        return True

    def __getitem__(self, key: str) -> Any:
        if not self.yaml_data:
            raise RuntimeError("YAML data not loaded")
        return self.yaml_processor.get_node_value(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if not self.yaml_data:
            raise RuntimeError("YAML data not loaded")
        self.yaml_processor.set_node_value(key, value)

    def __delitem__(self, key: str) -> None:
        if not self.yaml_data:
            raise RuntimeError("YAML data not loaded")
        self.yaml_processor.delete_node(key)

class AppContext(object):
    """
    The AppContext is a data container supporting inheritable configuration
    variables (settings or preferences) and Python context management for
    concurrency and resource management. It can be used in a "with" block
    to support nested subcommands, shells, tasks, etc.

    Conceptually this class is similar to the Context provided with Click
    and Typer CLI libraries, but unlike those it is a Python context manager
    as well as a data container. That said, this class works alongside
    the Click and Typer contexts and is not a replacement for them.
    """

    @staticmethod
    def get_default_config_path() -> Path | None:
        """
        Attempt to load the default YAML configuration for the specified
        package. This method can raise an exception, but allowing it to do
        so avoids the need for the method to be aware of the caller's
        logging and error handling design. The simple absence of a config
        file for a package is not considered an error.

        :param package: The name of the package. The package is not required
        to contain an __init__.py file.
        :return: A YAML object or None if the module has no default configuration file.
        """
        package_path = Path(__file__).parent
        config_path = package_path / 'default.yaml'
        return config_path
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __init__(self, parent: Optional["AppContext"] = None):
        self.parent = parent
        self.config: YAMLChainMap = YAMLChainMap()
        if parent:
            self.config.maps.append(parent.config)
        if __package__:
            self.config.load(AppContext.get_default_config_path())

