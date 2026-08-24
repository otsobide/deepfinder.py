"""Search values in nested structures using dot paths such as ``'users.0.name'``."""

from deepfinder.deep_find import deep_find
from deepfinder.entity import DeepFinderDict, DeepFinderList

__all__ = ['DeepFinderDict', 'DeepFinderList', 'deep_find']
__version__ = '1.6.0'
