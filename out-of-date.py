#!/usr/bin/env python

from __future__ import print_function

import sys

from e_ood.analyze import Analyzer
from e_ood.db import VersionDB
from e_ood.pypi import PackageVersionInfo
from e_ood.virtualenv import EnvPackages


def go(verbose=False):
    version_info = PackageVersionInfo()
    if len(sys.argv) == 2:
        env_packages = EnvPackages.from_freeze_file(sys.argv[1], verbose=verbose)
    else:
        env_packages = EnvPackages.from_active_env(verbose=verbose)
    version_db = VersionDB()
    analyzer = Analyzer(env_packages, version_info, version_db)
    output = analyzer.run()
    version_info.save()

    print(output)

    if analyzer.up_to_date:
        print('Up to date: %s' % ', '.join(analyzer.up_to_date))
    if env_packages.packages_with_error:
        print(
            'Packages with PyPI or version problem: %s' % ', '.join(
                sorted(env_packages.packages_with_error)
            )
        )


if __name__ == '__main__':
    go()
