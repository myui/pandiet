import logging
import pkg_resources

from . import (
  core
)

from .core import Reducer

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

