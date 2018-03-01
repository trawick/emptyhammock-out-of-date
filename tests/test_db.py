import os
import tempfile
import unittest

from six import StringIO

from e_ood.db import VersionDB


class TestDB(unittest.TestCase):

    def test_changelog(self):
        version_db = VersionDB()
        self.assertIsNone(version_db.get_changelog('FOOPACKAGE'))
        self.assertIsNone(version_db.get_changelog('____TEMPLATE'))
        self.assertEqual(
            'https://github.com/pallets/click/blob/master/CHANGES',
            version_db.get_changelog('click')
        )

    def test_ignore_compat_releases(self):
        version_db = VersionDB()
        vers = version_db.ignore_releases(
            'django-mptt', '0.0.1', ['0.8.7', '0.9.0'], ignore_compat_releases=True
        )
        self.assertEqual(['0.8.7'], vers)

    def test_ignore_alpha_releases(self):
        version_db = VersionDB()
        all_available_releases = ['3.3.0', '3.3.0rc1', '3.3.0b1', '3.3.0a1']
        vers = version_db.ignore_releases(
            'django-autocomplete-light', '1.0.0', all_available_releases,
        )
        self.assertEqual(['3.3.0'], vers)
        vers = version_db.ignore_releases(
            'django-autocomplete-light', '1.0.0', all_available_releases,
            ignore_alpha_beta_rc_releases=False,
        )
        self.assertEqual(all_available_releases, vers)

    def test_yaml_db_default(self):
        version_db = VersionDB()
        self.assertEqual(
            'https://github.com/mozilla/bleach/blob/master/CHANGES',
            version_db.get_changelog('bleach')
        )

    def test_yaml_db_object(self):
        db_text = """d:
  changelog_url: 'https://docs.d.com/CHANGELOG.md'
  bug_fix_releases: [1.11.9, 2.0, 2.0.1]
  compatibility_releases: []
  feature_releases: []
  ignored_releases: []
  security_releases: [1.11.10, 2.0.2]
  lts_releases: [1.11.]
"""
        version_db = VersionDB(yaml_db=StringIO(db_text))
        self.assertEqual(
            'https://docs.d.com/CHANGELOG.md',
            version_db.get_changelog('d')
        )

    def test_yaml_db_filename(self):
        db_text = """d:
  changelog_url: 'https://docs.d.com/CHANGELOG.md'
  bug_fix_releases: [1.11.9, 2.0, 2.0.1]
  compatibility_releases: []
  feature_releases: []
  ignored_releases: []
  security_releases: [1.11.10, 2.0.2]
  lts_releases: [1.11.]
"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            db_path = os.path.join(tmpdirname, 'test.yaml')
            with open(db_path, 'w') as f:
                f.write(db_text)
            version_db = VersionDB(yaml_db=db_path)
            self.assertEqual(
                'https://docs.d.com/CHANGELOG.md',
                version_db.get_changelog('d')
            )
