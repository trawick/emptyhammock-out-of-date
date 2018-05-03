""" Represent the user's database of version classifications. """
import os
import re

import yaml


class ReportedUpdateTypes(object):
    """
    Represent which types of updates are of interest to a client.
    """

    TYPE_TO_FLAGS = {
        'all': dict(
            ignore_alpha_beta_rc_releases=False,
            ignore_feature_releases=False,
            ignore_compat_releases=False,
            ignore_bug_fix_releases=False,
            ignore_security_releases=False,
        ),
        'feature': dict(
            ignore_alpha_beta_rc_releases=True,
            ignore_feature_releases=False,
            ignore_compat_releases=False,
            ignore_bug_fix_releases=False,
            ignore_security_releases=False,
        ),
        'compat': dict(
            ignore_alpha_beta_rc_releases=True,
            ignore_feature_releases=True,
            ignore_compat_releases=False,
            ignore_bug_fix_releases=False,
            ignore_security_releases=False,
        ),
        'bug': dict(
            ignore_alpha_beta_rc_releases=True,
            ignore_feature_releases=True,
            ignore_compat_releases=True,
            ignore_bug_fix_releases=False,
            ignore_security_releases=False,
        ),
        'security': dict(
            ignore_alpha_beta_rc_releases=True,
            ignore_feature_releases=True,
            ignore_compat_releases=True,
            ignore_bug_fix_releases=True,
            ignore_security_releases=False,
        ),
        'none': dict(
            ignore_alpha_beta_rc_releases=True,
            ignore_feature_releases=True,
            ignore_compat_releases=True,
            ignore_bug_fix_releases=True,
            ignore_security_releases=True,
        ),
    }

    def __init__(self, types=None):
        # explicitly set these to help static analysis
        self.ignore_alpha_beta_rc_releases = False
        self.ignore_feature_releases = False
        self.ignore_compat_releases = False
        self.ignore_bug_fix_releases = False
        self.ignore_security_releases = False

        types = types or 'bug'
        try:
            ignore_args = self.TYPE_TO_FLAGS[types]
        except KeyError:
            raise ValueError('Invalid types "%s"' % types)
        for k, value in ignore_args.items():
            setattr(self, k, value)

    def update(self, **kwargs):
        """
        Modify the types of new releases that should be reported.
        :param kwargs: ignore_XXX_releases=True|False
            where XXX is "alpha_beta_rc" or "feature" or "compat" or "bug_fix"
            or "security".  This call is only needed if a relatively odd
            combination of release types should be identified.
        :return:
        """
        valid_flags = self.TYPE_TO_FLAGS['none'].keys()
        for k, value in kwargs.items():
            if k not in valid_flags:
                raise ValueError('Invalid flag "%s" passed to update()' % k)
            if not isinstance(value, bool):
                raise ValueError('Invalid value "%s" for flag "%s" passed to update()' % (value, k))
            setattr(self, k, value)

    def is_reported(self, type_string):
        """
        Is this version type reported?
        :param type_string: 'alpha_beta_rc'|'feature'|'compat'|'bug_fix'|'security'
        :return: True if a version of this type should be reported
        """
        if type_string not in (
                'alpha_beta_rc', 'feature', 'compat', 'bug_fix', 'security'
        ):
            raise ValueError('Bad release type string "%s"' % type_string)

        return (
            type_string == 'alpha_beta_rc' and not self.ignore_alpha_beta_rc_releases or
            type_string == 'feature' and not self.ignore_feature_releases or
            type_string == 'compat' and not self.ignore_compat_releases or
            type_string == 'bug_fix' and not self.ignore_bug_fix_releases or
            type_string == 'security' and not self.ignore_security_releases
        )


class PackageVersionClassifications(object):
    """
    Represent the user's database of version classifications.
    """

    MAPPINGS = (
        ('bug_fix_releases', 'Non-security bug fixes'),
        ('compatibility_releases',
         'Adds compatibility for a new version of Python, Django, or other important package'),
        ('feature_releases', 'Adds new features'),
        ('security_releases', 'SECURITY'),
    )

    ALPHA_BETA_RC = re.compile(r'^[0-9.]+(a|b|rc)\d+$')

    def __init__(self, yaml_db=None):
        """
        :param yaml_db: optional YAML document, specified via a filename or
           file-like object
        """
        if yaml_db is None:
            yaml_db = os.path.join(
                os.path.dirname(__file__),
                'db.yaml'
            )
        if callable(getattr(yaml_db, 'read', None)):
            yaml_contents = yaml_db.read()
        else:
            with open(yaml_db) as db_file:
                yaml_contents = db_file.read()

        self._data = yaml.load(
            yaml_contents,
            # some version numbers, such as "2.0", look like float; disable
            # auto-conversion so that all version numbers are strings
            Loader=yaml.BaseLoader
        )

    def _get_entry(self, package_name):
        entry = self._data.get(package_name, None)
        if not entry:
            raise ValueError('No definition for package "%s"' % package_name)
        return entry

    def get_changelog(self, package_name):
        """
        Return URL of changelog for specified package, if recorded.

        :param package_name: package to check
        :return: URL string if found, or None if package not in db or no
            changelog for the package is in the db
        """
        try:
            entry = self._get_entry(package_name)
        except ValueError:
            return None
        return entry.get('changelog_url', None) or None

    def classify_release(self, package_name, version):
        """
        Return human-readable string for the classification of the specified
        version of the specified package.

        :param package_name: package to check
        :param version: version to check

        :return: either string describing the classification, or error message
            if the package wasn't found or if no information is available about
            the version
        """
        try:
            entry = self._get_entry(package_name)
        except ValueError:
            return 'No information about package'
        for k, human_readable in self.MAPPINGS:
            if version in [str(v) for v in entry[k]]:
                return human_readable
        return 'No information about version'

    def is_security_release(self, package_name, versions):
        """
        Check if any of specified versions of specified package are security
        releases.

        :param package_name: name of package to check
        :param versions: list of versions to check
        :return: boolean
        """
        if isinstance(versions, str):
            versions = [versions]
        entry = self._get_entry(package_name)
        for version in versions:
            if version in entry['security_releases']:
                return True
        return False

    def filter_available_releases(self, package_name, current_version, versions, types):
        """
        For a particular package + current_version + list of newer versions,
        reduce the list of newer versions to those of interest according to
        types.

        :param package_name: name of Python package
        :param current_version: version currently installed
        :param versions: iterable of newer versions
        :param types: instance of ReportedUpdateTypes, indicating which types
            of newer releases should be reported
        :return: list of the newer releases of interest according to types
        """
        entry = self._get_entry(package_name)

        def _ignorable(version):
            if version in entry['ignored_releases']:
                return True

            checks = (
                ('feature', version in entry['feature_releases']),
                ('bug_fix', version in entry['bug_fix_releases']),
                ('security', version in entry['security_releases']),
                ('compat', version in entry['compatibility_releases']),
                ('alpha_beta_rc', self.ALPHA_BETA_RC.match(version))
            )
            for check, condition in checks:
                if condition and not types.is_reported(check):
                    return True

            # If the current_version is an LTS release and the version being checked
            # doesn't match, then it must be higher -- and we don't care about it.
            for lts in entry['lts_releases']:
                if current_version[:len(lts)] == lts:  # environment is using this LTS release
                    if version[:len(lts)] != lts:  # version considered is not this LTS release
                        return True  # ignorable, since version not applicable

            return False

        return [
            v for v in versions if not _ignorable(str(v))
        ]
