import unittest

from six import StringIO

from e_ood.virtualenv import EnvPackages


class TestVirtualenv(unittest.TestCase):

    def test_listing(self):
        env = EnvPackages.from_freeze_file(StringIO('a===1.0.0'))
        packages = [p for p, _ in env]
        self.assertEqual(['a'], packages)

        env = EnvPackages.from_freeze_file(StringIO('a===1.0.0\nb===2.2.2\n'))
        packages = [p for p, _ in env]
        self.assertEqual(['a', 'b'], packages)
