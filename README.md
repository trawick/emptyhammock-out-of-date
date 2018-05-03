# out-of-date checking and reporting for Python packages

[![Build Status](https://travis-ci.org/trawick/emptyhammock-out-of-date.svg?branch=master)](https://travis-ci.org/trawick/emptyhammock-out-of-date)

## Target audience

Your team carefully tracks the versions of packages in your production virtualenvs
and assesses new releases of those packages to determine if, and how quickly, you
should upgrade.

This is not an instant solution for identifying vulnerabilities in your virtualenvs,
though you could use this library to build such a solution.  The distinction is that,
in general, the users of this library assess new releases.

## Synopsis

This package assists you with

* Finding out when a newer version of a package in your virtualenv is available
  from PyPI.
* Recording your determination of the criticality of the upgrade to that package.
* Reporting the packages in your virtualenv that need to be updated, and why.

You can use the package in contexts such as

* From your development environment, perhaps using the bundled command-line program
* From a maintenance bot that periodically pulls "pip freeze" reports from your
  production environments
* From your CI tasks, examining the virtualenv in new Docker images and triggering a
  failure when the image is missing a critical update

## Information used to analyze your virtualenv

* Your virtualenv's contents, either in the form of the output of `pip freeze`
  or examination of the active virtualenv
* PyPI, to find out when new package versions are available
  * cached for a configurable length of time
* Your package release database, in the form of a YAML file, that categorizes the
  releases of PyPI packages of interest by criticality

## Package release database

### Format

The database is a YAML dictionary that you maintain, with these attributes for
each included package:

```yaml
my-package-name:
  bug_fix_releases: []
  compatibility_releases: []
  feature_releases: []
  ignored_releases: []
  security_releases: []
  lts_releases: []
```

An actual example:

```yaml
Django:
  changelog_url: 'https://docs.djangoproject.com/en/2.0/releases/'
  bug_fix_releases: [1.11.9, 2.0, 2.0.1, 1.11.12]
  compatibility_releases: []
  feature_releases: []
  ignored_releases: []
  security_releases: [1.11.10, 2.0.2, 1.11.11]
  lts_releases: [1.11.]
```

A release of a package with a security fix should be listed **only** in
`security_releases`, any other releases with some other type of bug fix
should be listed only in `bug_fix_releases`, any other releases with changes to
accommodate new Python, Django, or other critical dependencies should be
listed only in `compatibility_releases`, etc.  `lts_releases` lists releases
of a package for which fixes for all critical problems are available.

#### LTS releases and bug fixes for later non-LTS releases

The Django example above illustrates this concept.  At the time of this writing, 1.11 is
the current LTS release and 2.0 is a non-LTS feature release.  New versions in
either the 1.11 or 2.0 series are included in `bug_fix_releases` or
`security_releases` as appropriate, and 1.11 is declared to be an LTS release.
Thus, if an environment is using 1.11.x (i.e., using the LTS release), then
only newer bug or security fix releases in the 1.11 series will be considered
critical.

For the Django LTS release 1.11, the LTS release is specified as `1.11.`,
which will match `1.11.anything`.  As an LTS release specification doesn't have
an expiration date, the spec must be removed from the database once the release
is no longer supported.  Otherwise, information about relevant newer releases for
environments still using the out-of-date LTS release would be suppressed.

### Default package release database

This package ships with a default database which serves as an example.  It will
be used unless your database is specified, either with the API or with the
command-line tool.

The default database contains only packages used by Emptyhammock projects, and
only for packages with new releases since this project was put to use.
Additionally, the version of the database in this package is almost always out
of date with the one used for the analysis of Emptyhammock virtualenvs.

## Django admin support for package release database

The companion package [emptyhammock-out-of-date-django](https://github.com/trawick/emptyhammock-out-of-date-django)
allows you to maintain the package database for your projects via the Django
admin, and export that database either from admin or via an HTTP request from
an authorized client.

## Dependencies

* Python: 2.7.recent, 3.5, 3.6, and 3.7 are supported.
* `Requests` and `PyYAML`

*Python 2.7 support will be dropped as soon as I update a few remaining
environments.*

## Installation

`emptyhammock-out-of-date` is not currently on PyPI, so it is installed from
GitHub as follows:

```
(virtualenv) $ pip install git+git://github.com/trawick/emptyhammock-out-of-date.git@0.1.99
```

Replace `0.1.99` with the latest release, visible on the
[release page](https://github.com/trawick/emptyhammock-out-of-date/releases).

## Running from the command-line

```
(virtualenv) $ out_of_date.py
certifi: 2018.1.18
Newer releases:
  2018.4.16: Non-security bug fixes

pycodestyle: 2.3.1
Newer releases:
  2.4.0: No information about package

Up to date: chardet, coverage, flake8, idna, mccabe, pluggy, py, pyflakes, PyYAML, requests, requests-mock, six, tox, urllib3, virtualenv
```

*In this example, `pycodestyle` is not defined in the package release
database.*

## Using the API

```python
from e_ood import Analyzer, EnvPackages, AvailablePackageVersions, PackageVersionClassifications

env_packages = EnvPackages.from_freeze_file('production-freeze.txt')
version_db = PackageVersionClassifications(yaml_db='/path/to/your/db.yaml')
with AvailablePackageVersions() as version_info:
    analyzer = Analyzer(env_packages, version_info, version_db)
    result = analyzer.analyze()
output = result.render()
if output:
    print('Out of date packages for foo.com:')
    print()
    print(output)
```

Just see security fixes:

```
...
result = analyzer.analyze(types=ReportedUpdateTypes('security')
...
```

## Support

Please open Github issues for suggestions or suspected problems.  Even if I am
unable to respond in a timely basis, the information may quickly become valuable
to others, and I will eventually find time to respond to the issue.
