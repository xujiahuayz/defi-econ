from os import path
from environ.settings import PROJECT_ROOT

BOOM_BUST = {
    "boom": [(1469966400, 1472558500), (1469966800, 1469966900)],
    "bust": [(1472558500, 1475150600), (1469966900, 1469967000)],
}

FIGURE_PATH = path.join(PROJECT_ROOT, "figures")
