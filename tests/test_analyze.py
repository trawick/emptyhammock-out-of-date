import os
import unittest

from six import StringIO

from e_ood import Analyzer, EnvPackages, VersionDB


TEST_DB_NAME = os.path.join(os.path.dirname(__file__), 'test_db.yaml')
NON_LTS_EXAMPLE_VERSIONS = [
    '1.0.1', '1.0.2', '1.0.3', '1.0.4', '1.0.5', '1.0.6', '1.0.7', '1.0.7a1',
    '1.0.7b2', '1.0.8', '1.0.8rc3'
]


class FakePackageVersionInfo(object):
    """
    This class mimics the PyPI representation (AvailablePackageVersions), in order to
    * avoid hitting PyPI while running tests
    * test with fixed data
    """
    def __init__(self, version_info=None):
        self.version_info = version_info or {}

    def get(self, package_name):
        return self.version_info.get(package_name)

    @classmethod
    def from_list(cls, package_name, versions):
        data = {
            package_name: {
                'releases': {
                    v: True
                    for v in versions
                }
            }
        }
        return cls(data)


class TestAnalyze(unittest.TestCase):

    def test_lts(self):
        env = EnvPackages.from_freeze_file(StringIO('d===1.11.5'))
        version_db = VersionDB(yaml_db=TEST_DB_NAME)
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
        report = analyzer.analyze()
        expected_report = """d: 1.11.5
Newer releases:
  1.11.9: Non-security bug fixes
  1.11.10: SECURITY
  Changelog: https://docs.d.com/CHANGELOG.md
"""
        self.assertEqual(expected_report, report.render())

    def test_report_older(self):
        env = EnvPackages.from_freeze_file(StringIO('non-lts-example==1.0.7'))
        version_db = VersionDB(yaml_db=TEST_DB_NAME)
        available = FakePackageVersionInfo.from_list('non-lts-example', NON_LTS_EXAMPLE_VERSIONS)
        analyzer = Analyzer(env, available, version_db)
        report = analyzer.analyze()
        # non-verbose:
        expected_report = """non-lts-example: 1.0.7
Newer releases:
  1.0.8: SECURITY
  Changelog: https://non-lts-example.com/CHANGES.md
"""
        self.assertEqual(expected_report, report.render())
        # verbose: (should show older releases)
        expected_report = """non-lts-example: 1.0.7
Newer releases:
  1.0.8: SECURITY
  Changelog: https://non-lts-example.com/CHANGES.md
Older: 1.0.1, 1.0.2, 1.0.3, 1.0.4, 1.0.5, 1.0.6, 1.0.7a1, 1.0.7b2
"""
        self.assertEqual(expected_report, report.render(verbose=True))

    def test_report_ignore_all(self):
        env = EnvPackages.from_freeze_file(StringIO('non-lts-example==1.0.7'))
        version_db = VersionDB(yaml_db=TEST_DB_NAME)
        available = FakePackageVersionInfo.from_list('non-lts-example', NON_LTS_EXAMPLE_VERSIONS)
        analyzer = Analyzer(env, available, version_db)
        report = analyzer.analyze(
            ignored_packages=['non-lts-example']
        )
        self.assertEqual('', report.render())

    def test_report_no_newer(self):
        env = EnvPackages.from_freeze_file(StringIO('non-lts-example==1.0.8'))
        version_db = VersionDB(yaml_db=TEST_DB_NAME)
        available = FakePackageVersionInfo.from_list('non-lts-example', NON_LTS_EXAMPLE_VERSIONS)
        analyzer = Analyzer(env, available, version_db)
        report = analyzer.analyze()
        # non-verbose:
        expected_report = ''
        self.assertEqual(expected_report, report.render())
        # verbose: (should show older releases)
        expected_report = """non-lts-example: 1.0.8
Older: 1.0.1, 1.0.2, 1.0.3, 1.0.4, 1.0.5, 1.0.6, 1.0.7a1, 1.0.7b2, 1.0.7, 1.0.8rc3

Up to date: non-lts-example
"""
        self.assertEqual(expected_report, report.render(verbose=True))

    def test_unknown_package(self):
        env = EnvPackages.from_freeze_file(StringIO('FOO==1.0.8'))
        version_db = VersionDB(yaml_db=TEST_DB_NAME)
        available = FakePackageVersionInfo()
        analyzer = Analyzer(env, available, version_db)
        report = analyzer.analyze()
        expected_report = """Packages with PyPI or version problem: FOO
"""
        self.assertEqual(expected_report, report.render())

    def test_package_not_in_release_database(self):
        env = EnvPackages.from_freeze_file(StringIO('FOO==1.0.8'))
        version_db = VersionDB(yaml_db=TEST_DB_NAME)
        available = FakePackageVersionInfo.from_list('FOO', ['1.0.8', '1.0.9'])
        analyzer = Analyzer(env, available, version_db)
        report = analyzer.analyze()
        expected_report = """FOO: 1.0.8
Newer releases:
  1.0.9: No information about package
"""
        self.assertEqual(expected_report, report.render())
