# Changes and migration requirements

## Version 0.1.39

* Analysis no longer fails to report packages that have newer versions but
  which aren't listed in the package release database.

## Version 0.1.38

### Breaking changes

* Optional freeze output is passed to `out_of_date.py` as a normal argument,
  instead of using `--frozen` option.

### Other changes

* Analysis report rendering: Suppress verbose info unless verbose is specified
  or there are also problems to report.
* Ignore blank lines and "#" comments in freeze files.
* `PackageVersionInfo` supports a context manager, to avoid having to call
  `save()` after looking up version information.
* `EnvPackages` supports multiple concurrent iterators.

## Version 0.1.37

* Fix packaging issue encountered when installing into virtualenvs
  without `yaml` and `requests`.

## Version 0.1.36

### Breaking changes

* Script renamed to `out_of_date.py`.
* New class `ReportedUpdateTypes` is used to indicate which types of available
  releases should be reported.  This affects all clients.
* `out-of-date.py` syntax changed for invocations with a `pip freeze`
  file.
* `analyze()` now returns an `AnalyzerReport` object instead of a formatted
  report.  Use the `render()` object on the report object to get a formatted
  report, or inspect the report object for custom checks or reporting.

### Other changes

* All imports can (and should) be imported from the package ()`e_ood`) instead
  of individual modules within the package.
* `out-of-date.py` now has command-line arguments to configure most aspects
  of operation.
* Fix bug in handling of string passed to `is_security_release()`.
* Fix bug in handling of optional `yaml_db` parameter to `VersionDB()`.
* Updates to the default package db.
* PyPI cache file isn't left opened.

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
* six is now a required development dependency.

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
