import os

import yaml


class VersionDB(object):

    MAPPINGS = (
        ('bug_fix_releases', 'Non-security bug fixes'),
        ('compatibility_releases', 'Adds compatibility for a new version of Python, Django, or other important package'),
        ('feature_releases', 'Adds new features'),
        ('security_releases', 'SECURITY'),
    )

    def __init__(self, yaml_db=None):
        if not yaml_db:
            yaml_db = os.path.join(
                os.path.dirname(__file__),
                'db.yaml'
            )
        self.db = yaml.load(
            open(yaml_db).read(),
            # some version numbers, such as "2.0", look like float; disable
            # auto-conversion so that all version numbers are strings
            Loader=yaml.BaseLoader
        )

    def _get_entry(self, package_name):
        entry = self.db.get(package_name, None)
        if not entry:
            raise ValueError('No definition for package "%s"' % package_name)
        return entry

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

    @staticmethod
    def _ignorable(entry, version, ignore_feature_releases):
        if version in entry['ignored_releases']:
            return True
        if ignore_feature_releases and version in entry['feature_releases']:
            return True
        return False

    def ignore_releases(self, package_name, versions, ignore_feature_releases=False):
        entry = self._get_entry(package_name)
        return [
            v for v in versions
            if not self._ignorable(entry, str(v), ignore_feature_releases)
        ]