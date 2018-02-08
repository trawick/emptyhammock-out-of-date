# Changes and migration requirements

## Versions 0.1.16 through 0.1.29

* Updates to the default package db (only)

## Version 0.1.15

* `EnvPackages()` recovers when a package/version string can't be parsed.
* PyPI interface now caches package-not-found (404 error from PyPI).
* PyPI logs a non-200/non-404 result instead of printing to stdout.
* Updates to the default package db
* `setup.py`: Specify dependencies `requests` and `PyYAML` as dependencies.
* Windows platform: Fix bug finding user directory (for finding `.pyold.json`).

## Version 0.1.14

* Available alpha/beta/release-candidate releases are ignored by default when
  comparing installed versions against the package database, as long as the
  version strings follow the usual convention (ending in rcNUMBER, aNUMBER,
  or bNUMBER).
