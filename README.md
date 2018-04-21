# out-of-date checking and reporting for Python packages

## Current state

* `master` has a bunch of untagged changes which amount to a large refactor.
  Short term plans:
  * Rename out-of-date.py to use underscores instead of hyphens
  * Improve test coverage
  * Tag

## Synopsis

Assist you with

* finding out when a newer version of a package in your virtualenv is available
  from PyPI
* storing your determination of the criticality of the upgrade to that package
* reporting the packages in your virtualenv that need to be updated, and why

## Target audience

You carefully track the versions of packages in your virtualenv and assess new
releases to determine if you should upgrade, and how quickly.

## Components

* your virtualenv's contents, either in the form of the output of `pip freeze`
  or examination of the virtualenv when this library is used
* access to PyPI, to find out when new package versions are available
  * cached for a configurable length of time
* a package release database, in the form of a YAML file, that categorizes the
  releases of PyPI packages of interest by criticality
  * e.g., covering the *N* packages used by your *M* projects

## Package release database

### Format

The database is a YAML dictionary, with these attributes for each included
package:

```
my-package-name:
  bug_fix_releases: []
  compatibility_releases: []
  feature_releases: []
  ignored_releases: []
  security_releases: []
  lts_releases: []
```

Any release of the package with a security fix will be listed **only** in
`security_releases`, any other releases with some other type of bug fix
will be listed only in `bug_fix_releases`, any other releases with changes to
accommodate new Python, Django, or other critical dependencies will be
listed only in `compatibility_releases`, etc.  `lts_releases` lists releases
of a package for which fixes for all critical problems are available.  From
this a report of the most critical version issues can be created.

#### LTS releases and bug fixes for later non-LTS releases

Django is the obvious example for this.  At the time of this writing, 1.11 is
the current LTS release and 2.0 is a non-LTS feature release.  New versions in
either the 1.11 or 2.0 series are included in `bug_fix_releases` or
`security_releases` as appropriate, and 1.11 is declared to be an LTS release.
Thus, if an environment is using 1.11.x (i.e., using the LTS release), then
only newer bug or security fix releases in the 1.11 series will be considered
critical.

Using Django 1.11 as an example again, the LTS release is specified as `1.11.`,
which will match `1.11.anything`.  As an LTS release specification doesn't have
an expiration date, the spec must be removed once the release is no longer
supported to avoid suppressing information about relevant newer releases for
environments still using the out-of-date LTS release.

### Default database

This package ships with a default database which is useful as an example.
The database contains only packages used by Emptyhammock projects, and only for
versions of those packages released since this project was put to use.
Additionally, the version of the database in this package is almost always out
of date with the one used for the analysis of Emptyhammock virtualenvs.

## Django admin support

The companion package [emptyhammock-out-of-date-django](https://github.com/trawick/emptyhammock-out-of-date-django)
allows you to maintain the package database for your projects via the Django
admin, and export that database either from admin or via an HTTP request from
an authorized client.

## Dependencies

* Python: 2.7.recent, 3.5, 3.6, and 3.7 are supported.
* `Requests` and `PyYAML`
