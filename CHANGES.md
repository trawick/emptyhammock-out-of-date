# Changes and migration requirements

## Version 0.1.15 (not yet released)

* Updates to the default package db
* `setup.py`: Specify dependencies `requests` and `PyYAML` as dependencies.
* Windows platform: Fix bug finding user directory (for finding `.pyold.json`).

## Version 0.1.14

* Available alpha/beta/release-candidate releases are ignored by default when
  comparing installed versions against the package database, as long as the
  version strings follow the usual convention (ending in rcNUMBER, aNUMBER,
  or bNUMBER).
