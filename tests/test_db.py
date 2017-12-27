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
            'django-mptt', ['0.8.7', '0.9.0'], ignore_compat_releases=True
        )
        self.assertEqual(['0.8.7'], vers)
