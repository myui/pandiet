import logging
import pkg_resources

from . import (
  core
)

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    pass

