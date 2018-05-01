#!/usr/bin/env python
"""Command-line interface to out-of-date library"""

from __future__ import print_function

import argparse
import re
import sys

from e_ood import Analyzer, EnvPackages, PackageVersionInfo, ReportedUpdateTypes, VersionDB


def main():
    """Parse arguments and analyze"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--cache-file',
        help='name of JSON document where data from PyPI is cached'
    )
    parser.add_argument('--cache-time', help='seconds that data from PyPI is cached',
                        type=int)
    parser.add_argument('--db', help='path to package release database')
    parser.add_argument('--ignore', help='comma-delimited list of packages to ignore', default='')
    parser.add_argument('--types', help='all|feature|compat|bug|security')
    parser.add_argument('--verbose', help='show more details',
                        action='store_true')
    parser.add_argument('freeze_output', nargs='?')
    args = parser.parse_args()

    if args.freeze_output:
        env_packages = EnvPackages.from_freeze_file(args.freeze_output)
    else:
        env_packages = EnvPackages.from_active_env()
    if env_packages.packages_with_error:
        print('Packages in virtualenv with error:')
        for package in env_packages.packages_with_error:
            print('  %s' % package)
        print()

    version_db = VersionDB(yaml_db=args.db)

    try:
        types = ReportedUpdateTypes(types=args.types)
    except ValueError:
        print('Bad value for --types', file=sys.stderr)
        sys.exit(1)

    split_re = re.compile('( +| *, *)')
    with PackageVersionInfo(
        max_pypi_age_seconds=args.cache_time,
        pypi_cache_file=args.cache_file
    ) as version_info:
        analyzer = Analyzer(env_packages, version_info, version_db)
        report = analyzer.analyze(
            ignored_packages=split_re.split(args.ignore),
            types=types,
        )

    print(report.render(verbose=args.verbose))


if __name__ == '__main__':
    main()
