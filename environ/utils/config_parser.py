"""
Parsing configuration files.
"""

# Import standard python modules
import os
import sys
import logging

# Import other python modules
from collections import UserDict


import yaml
from yaml import YAMLError

# from ruamel import yaml
# from ruamel.yaml.scanner import ScannerError

logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

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
                except YAMLError as e_yaml:
                    log.error(
                        "Error parsing YAML config file %s: %s",
                        self.config_path,
                        e_yaml,
                    )
        except FileNotFoundError:
            log.error("YAML file not found in %s", self.config_path)
            sys.exit(1)
