#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys

from e_ood.analyze import Analyzer
from e_ood.db import VersionDB, ReportedUpdateTypes
from e_ood.pypi import PackageVersionInfo
from e_ood.virtualenv import EnvPackages


def go():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    parser.add_argument('--cache-time', help='seconds that data from PyPI is cached',
                        type=int)
    parser.add_argument('--db', help='path to package release database')
    parser.add_argument('--frozen', help='path to "pip freeze" output')
    parser.add_argument('--ignore', help='comma-delimited list of packages to ignore', default='')
    parser.add_argument('--types', help='feature|compat|bug|security')
    parser.add_argument('--verbose', help='show more details',
                        action='store_true')
    args = parser.parse_args()

    version_info = PackageVersionInfo(max_pypi_age_seconds=args.cache_time)
    if args.frozen:
        env_packages = EnvPackages.from_freeze_file(args.frozen, verbose=args.verbose)
    else:
        env_packages = EnvPackages.from_active_env(verbose=args.verbose)
    version_db = VersionDB(yaml_db=args.db)

    try:
        types = ReportedUpdateTypes(types=args.types)
    except ValueError:
        print('Bad value for --types', file=sys.stderr)
        sys.exit(1)

    analyzer = Analyzer(env_packages, version_info, version_db)
    output = analyzer.analyze(
        ignored_packages=args.ignore.split(', '),
        types=types,
    )
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
