# out-of-date checking for Python packages

## Scope

Currently the database contains only packages used by some Emptyhammock projects,
and only for versions of those packages current when the project was first set up.
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
```

Any release of the package with a security fix will be listed **only** in
`security_releases`, any other releases with some other type of bug fix
will be listed only in `bug_fix_releases`, any other releases with changes to
accommodate new Python, Django, or other critical dependencies will be
listed only in `compatibility_releases`, etc.  From this a report of the most
critical version issues can be created.

### LTS releases and bug fixes for later non-LTS releases

Django is the obvious example for this.  At the time of this writing, 1.11 is
the current LTS release and 2.0 is a non-LTS feature release.  1.11.x releases
are included in `bug_fix_releases` or `security_releases` as appropriate, but
2.0.x releases are all included in `feature_releases`, like `2.0` itself.  This
results in out-of-date being reported only for new 1.11.x releases, not for
new 2.0.x releases.  A better concept, such as a list of LTS releases (e.g.
`lts_release_patterns: [1\.11\.\d+]`) could be used to avoid this kludge.
(The pattern for 1.11.x would be removed once it is no longer supported.)

## Dependencies

Python 2.7 and Python 3.x from Ubuntu >= 16.04 are supported.
