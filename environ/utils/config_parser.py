"""

University College London
Project : defi_econ
Topic   : config_parser
Author  : Yichen Luo
Date    : 2022-12-17
Desc    : function to parse the configuration.

"""

# Import standard python modules
import os
import sys
import logging

# Import other python modules
from collections import UserDict
from ruamel import yaml
from ruamel.yaml.scanner import ScannerError


log = logging.getLogger(__name__)


class Config(UserDict):

    """
    Arguments:
        config_path (str): Path to the configuration file.
        Default: ./properties/conf.yaml

    Public methods:
        load: Loads configuration from configuration YAML file.

    Attributes and properties:
        config_path (str): Path to the configuration file.
        data(dict): Program configuration.
    """

    def __init__(self, config_path="config/conf.yaml"):
        super().__init__()
        self.config_path = os.path.expanduser(config_path)
        self.load()

    def load(self):

        """
        loads config from yaml file
        """

        try:
            with open(os.path.expanduser(self.config_path), "r", encoding="utf-8") as f:
                try:
                    self.data = yaml.safe_load(f)
                except ScannerError as e_yaml:
                    log.error(
                        "Error parsing YAML config file " "%s:%s",
                        e_yaml.problem_mark,
                        e_yaml.problem,
                    )
                    sys.exit(1)
        except FileNotFoundError:
            log.error("YAML file not found in %s", self.config_path)
            sys.exit(1)
