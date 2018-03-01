# Changes and migration requirements

## Version 0.1.36 (unreleased)

* Fix bug in handling of optional yaml_db parameter to VersionDB().

## Version 0.1.35

* Change "LTS" release concept to use partial version strings like "1.11."
  instead of regular expressions.
* Updates to the default package db

## Version 0.1.34

* Add "LTS release" concept.  If the current version of a package matches a
  configured LTS release for the package, any fixes for later releases won't
  be considered applicable.
* Updates to the default package db

## Version 0.1.31 through 0.1.33

* Updates to the default package db (only)

## Version 0.1.30

* Updates to the default package db
* Fix a bug that could result in the last package listed in the virtualenv
  being reported twice.
* six is now a required dependency.

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
