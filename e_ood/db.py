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
        types = types or 'bug'
        try:
            ignore_args = self.TYPE_TO_FLAGS[types]
        except KeyError:
            raise ValueError('Invalid types "%s"' % types)
        for k, value in ignore_args.items():
            setattr(self, k, value)

    def update(self, **kwargs):
        valid_flags = self.TYPE_TO_FLAGS['none'].keys()
        for k, v in kwargs.items():
            if k not in valid_flags:
                raise ValueError('Invalid flag "%s" passed to update()' % k)
            if type(v) != bool:
                raise ValueError('Invalid value "%s" for flag "%s" passed to update()' % (v, k))
            setattr(self, k, v)


class VersionDB(object):

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
            with open(yaml_db) as f:
                yaml_contents = f.read()

        self.db = yaml.load(
            yaml_contents,
            # some version numbers, such as "2.0", look like float; disable
            # auto-conversion so that all version numbers are strings
            Loader=yaml.BaseLoader
        )

    def _get_entry(self, package_name):
        entry = self.db.get(package_name, None)
        if not entry:
            raise ValueError('No definition for package "%s"' % package_name)
        return entry

    def get_changelog(self, package_name):
        try:
            entry = self._get_entry(package_name)
        except ValueError:
            return None
        return entry.get('changelog_url', None) or None

    def classify_release(self, package_name, version):
        try:
            entry = self._get_entry(package_name)
        except ValueError:
            return 'No information about package'
        for k, human_readable in self.MAPPINGS:
            if version in [str(v) for v in entry[k]]:
                return human_readable
        return 'No information about version'

    def is_security_release(self, package_name, versions):
        if isinstance(versions, str):
            versions = [versions]
        entry = self._get_entry(package_name)
        for version in versions:
            if version in entry['security_releases']:
                return True
        return False

    def filter_available_releases(self, package_name, current_version, versions, types):
        entry = self._get_entry(package_name)

        def _ignorable(version):
            if version in entry['ignored_releases']:
                return True
            if types.ignore_feature_releases and version in entry['feature_releases']:
                return True
            if types.ignore_bug_fix_releases and version in entry['bug_fix_releases']:
                return True
            if types.ignore_security_releases and version in entry['security_releases']:
                return True
            if types.ignore_compat_releases and version in entry['compatibility_releases']:
                return True
            if types.ignore_alpha_beta_rc_releases and self.ALPHA_BETA_RC.match(version):
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
