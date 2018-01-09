import os
import re

import yaml


class VersionDB(object):

    MAPPINGS = (
        ('bug_fix_releases', 'Non-security bug fixes'),
        ('compatibility_releases', 'Adds compatibility for a new version of Python, Django, or other important package'),
        ('feature_releases', 'Adds new features'),
        ('security_releases', 'SECURITY'),
    )

    ALPHA_BETA_RC = re.compile(r'^[0-9.]+(a|b|rc)\d+$')

    def __init__(self, yaml_db=None):
        if not yaml_db:
            yaml_db = os.path.join(
                os.path.dirname(__file__),
                'db.yaml'
            )
        with open(yaml_db) as f:
            self.db = yaml.load(
                f.read(),
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
            versions = [str]
        entry = self._get_entry(package_name)
        for version in versions:
            if version in entry['security_releases']:
                return True
        return False

    def _ignorable(self, entry, version, ignore_feature_releases, ignore_compat_releases, ignore_alpha_beta_rc_releases):
        if version in entry['ignored_releases']:
            return True
        if ignore_feature_releases and version in entry['feature_releases']:
            return True
        if ignore_compat_releases and version in entry['compatibility_releases']:
            return True
        if ignore_alpha_beta_rc_releases and self.ALPHA_BETA_RC.match(version):
            return True

        return False

    def ignore_releases(self, package_name, versions, ignore_feature_releases=False,
                        ignore_compat_releases=False, ignore_alpha_beta_rc_releases=True):
        entry = self._get_entry(package_name)
        return [
            v for v in versions
            if not self._ignorable(entry, str(v), ignore_feature_releases, ignore_compat_releases, ignore_alpha_beta_rc_releases)
        ]
