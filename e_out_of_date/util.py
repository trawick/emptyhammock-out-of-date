import warnings

from pkg_resources import PkgResourcesDeprecationWarning


def ignore_pkg_resources_warnings():
    warnings.filterwarnings("ignore", category=PkgResourcesDeprecationWarning)
