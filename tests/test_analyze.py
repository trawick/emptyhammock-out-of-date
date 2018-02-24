import unittest

from six import StringIO

from e_ood.analyze import Analyzer
from e_ood.db import VersionDB
from e_ood.virtualenv import EnvPackages


class FakePackageVersionInfo(object):
    def __init__(self, version_info):
        self.version_info = version_info

    def get(self, package_name):
        return self.version_info[package_name]


class TestAnalyze(unittest.TestCase):

    def test_lts(self):
        db_text = """d:
  changelog_url: 'https://docs.d.com/CHANGELOG.md'
  bug_fix_releases: [1.11.9, 2.0, 2.0.1]
  compatibility_releases: []
  feature_releases: []
  ignored_releases: []
  security_releases: [1.11.10, 2.0.2]
  lts_release_patterns: [1\.11\.\d+]
"""
        env = EnvPackages.from_freeze_file(StringIO('d===1.11.5'))
        version_db = VersionDB(yaml_db=StringIO(db_text))
        available = FakePackageVersionInfo({
            'd': {
                'releases': {
                    '1.11.9': True,
                    '1.11.10': True,
                    '2.0': True,
                    '2.0.1': True,
                    '2.0.2': True
                }
            }
        })
        analyzer = Analyzer(env, available, version_db)
        actual_report = analyzer.analyze()
        expected_report = """d: 1.11.5
Newer releases:
  1.11.9: Non-security bug fixes
  1.11.10: SECURITY
  Changelog: https://docs.d.com/CHANGELOG.md
"""
        self.assertEqual(expected_report, actual_report)
