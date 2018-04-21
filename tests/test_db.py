import os
import re
import tempfile
import unittest

from six import StringIO

from e_ood.db import ReportedUpdateTypes, VersionDB


TEST_DB_CONTENTS = open(
    os.path.join(os.path.dirname(__file__), 'test_db.yaml')
).read()
NON_LTS_EXAMPLE_VERSIONS = [
    '1.0.1', '1.0.2', '1.0.3', '1.0.4', '1.0.5', '1.0.6', '1.0.7', '1.0.7a1',
    '1.0.7b2', '1.0.8', '1.0.8rc3'
]


class TestHandlingOfDB(unittest.TestCase):
    """
    Several testcases that check the use of
    * default db
    * override db specified via file handle
    * override db specified via file name
    """
    def test_yaml_db_default(self):
        version_db = VersionDB()
        self.assertEqual(
            'https://github.com/mozilla/bleach/blob/master/CHANGES',
            version_db.get_changelog('bleach')
        )

    def test_yaml_db_object(self):
        version_db = VersionDB(yaml_db=StringIO(TEST_DB_CONTENTS))
        self.assertEqual(
            'https://docs.d.com/CHANGELOG.md',
            version_db.get_changelog('d')
        )

    def test_yaml_db_filename(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            db_path = os.path.join(tmpdirname, 'test.yaml')
            with open(db_path, 'w') as f:
                f.write(TEST_DB_CONTENTS)
            version_db = VersionDB(yaml_db=db_path)
            self.assertEqual(
                'https://docs.d.com/CHANGELOG.md',
                version_db.get_changelog('d')
            )


class TestDB(unittest.TestCase):

    def setUp(self):
        self.db = VersionDB(yaml_db=StringIO(TEST_DB_CONTENTS))

    def test_bad_arg_recognition(self):
        with self.assertRaises(ValueError):
            ReportedUpdateTypes('foo')
        types = ReportedUpdateTypes()
        with self.assertRaises(ValueError):
            types.update(foo=True)
        with self.assertRaises(ValueError):
            types.update(ignore_feature_releases=0)

    def test_good_args(self):
        ReportedUpdateTypes('bug').update(ignore_bug_fix_releases=True)

    def test_changelog(self):
        self.assertEqual(
            'https://non-lts-example.com/CHANGES.md',
            self.db.get_changelog('non-lts-example')
        )

    def test_changelog_for_missing_package(self):
        self.assertEqual(None, self.db.get_changelog('NO-SUCH-PACKAGE'))

    def test_mode_security(self):
        types = ReportedUpdateTypes(types='security')
        versions = self.db.filter_available_releases(
            'non-lts-example', '1.0.0', NON_LTS_EXAMPLE_VERSIONS, types
        )
        self.assertEqual(['1.0.5', '1.0.8'], versions)

    def test_mode_report_nothing(self):
        types = ReportedUpdateTypes(types='security')
        types.update(ignore_security_releases=True)  # nothing left!
        versions = self.db.filter_available_releases(
            'non-lts-example', '1.0.0', NON_LTS_EXAMPLE_VERSIONS, types
        )
        self.assertEqual([], versions)

    def test_ignore_compat_releases(self):
        types = ReportedUpdateTypes(types='all')
        types.update(ignore_compat_releases=True)
        versions = self.db.filter_available_releases(
            'non-lts-example', '1.0.0', NON_LTS_EXAMPLE_VERSIONS, types
        )
        self.assertEqual([
            '1.0.2', '1.0.4', '1.0.5', '1.0.7', '1.0.7a1',
            '1.0.8', '1.0.8rc3'
        ], versions)

    def test_ignore_alpha_releases(self):
        types = ReportedUpdateTypes(types='all')
        types.update(ignore_alpha_beta_rc_releases=False)
        versions = self.db.filter_available_releases(
            'non-lts-example', '1.0.0', NON_LTS_EXAMPLE_VERSIONS, types
        )
        self.assertEqual([
            v for v in NON_LTS_EXAMPLE_VERSIONS
            if v != '1.0.1'
        ], versions)

        types = ReportedUpdateTypes(types='all')
        types.update(ignore_alpha_beta_rc_releases=True)
        versions = self.db.filter_available_releases(
            'non-lts-example', '1.0.0', NON_LTS_EXAMPLE_VERSIONS, types
        )
        self.assertEqual([
            v for v in NON_LTS_EXAMPLE_VERSIONS
            if v != '1.0.1' and not re.match(r'.*(a|b|rc)\d+$', v)
        ], versions)

    def test_classify_invalid_package(self):
        s = self.db.classify_release('foo-package', '1.8.5')
        self.assertTrue(s.startswith('No '))

    def test_classify_invalid_release(self):
        s = self.db.classify_release('non-lts-example', '99.99.99')
        self.assertTrue(s.startswith('No '))

    def test_valid_classify_release(self):
        s = self.db.classify_release('non-lts-example', '1.0.3')
        self.assertTrue(s.startswith('Adds compatibility '))

    def test_is_security_release_invalid_package(self):
        with self.assertRaises(ValueError):
            self.db.is_security_release('foo-package', '1.0.5')

    def test_is_security_release_true(self):
        self.assertTrue(self.db.is_security_release('non-lts-example', '1.0.8'))
        self.assertTrue(self.db.is_security_release('non-lts-example', ['1.0.8']))
        self.assertTrue(self.db.is_security_release('non-lts-example', ['1.0.1', '1.0.8']))

    def test_is_security_release_false(self):
        self.assertFalse(self.db.is_security_release('non-lts-example', '1.0.1'))
        self.assertFalse(self.db.is_security_release('non-lts-example', ['1.0.1']))
