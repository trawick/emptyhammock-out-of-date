# out-of-date checking for Python packages

## Synopsis

Report newer available versions of Python packages in an environment, classified
by the criticality of the update.  This is based on examination of the current
environment (or the equivalent of `pip freeze` from a different environment), a
database that classifies releases by criticality, and access to PyPI.

## Target audience

This package is useful for people that want to assess the criticality to their
project of package upgrades once new versions are available on PyPI.  This
package provides a framework for getting reports of new versions and classifying
those versions.

## Scope of default database

Currently the database contains only packages used by some Emptyhammock projects,
and only for versions of those packages current since the project was first set up.
It could conceivably be used for non-Emptyhammock projects with the addition of
more package definitions.

The determinations that can be made for out-of-date packages follow the template
at the top of `db.yaml`:

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

### LTS releases and bug fixes for later non-LTS releases

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

## Django admin support

The companion package [emptyhammock-out-of-date-django](https://github.com/trawick/emptyhammock-out-of-date-django)
allows you to maintain the package database for your projects via the Django
admin, and export that database either from admin or via an HTTP request from
an authorized client.

## Dependencies

Python 2.7 and Python 3.x from Ubuntu >= 16.04 are supported.
