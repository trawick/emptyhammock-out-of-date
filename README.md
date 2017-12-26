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

## Dependencies

Python 2.7 and Python 3.x from Ubuntu >= 16.04 are supported.
