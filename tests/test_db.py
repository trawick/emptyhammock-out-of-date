import unittest

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
