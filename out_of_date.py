#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys

from e_ood import Analyzer, EnvPackages, PackageVersionInfo, ReportedUpdateTypes, VersionDB


def go():
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

    version_info = PackageVersionInfo(
        max_pypi_age_seconds=args.cache_time,
        pypi_cache_file=args.cache_file
    )

    if args.freeze_output:
        env_packages = EnvPackages.from_freeze_file(args.freeze_output, verbose=args.verbose)
    else:
        env_packages = EnvPackages.from_active_env(verbose=args.verbose)
    if env_packages.packages_with_error:
        print('Packages in virtualenv with error: %s' % '\n'.join(
            env_packages.packages_with_error
        ))

    version_db = VersionDB(yaml_db=args.db)

    try:
        types = ReportedUpdateTypes(types=args.types)
    except ValueError:
        print('Bad value for --types', file=sys.stderr)
        sys.exit(1)

    analyzer = Analyzer(env_packages, version_info, version_db)
    report = analyzer.analyze(
        ignored_packages=args.ignore.split(', '),
        types=types,
    )
    version_info.save()

    print(report.render())


if __name__ == '__main__':
    go()
