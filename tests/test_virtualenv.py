import os
import shutil
import tempfile
import unittest

from six import StringIO

from e_ood import EnvPackages


class TestReadMechanisms(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_listing_from_readable(self):
        env = EnvPackages.from_freeze_file(StringIO('a===1.0.0'))
        packages = [p for p, _ in env]
        self.assertEqual(['a'], packages)

        env = EnvPackages.from_freeze_file(StringIO('a===1.0.0\nb===2.2.2\n'))
        packages = [p for p, _ in env]
        self.assertEqual(['a', 'b'], packages)

    def test_listing_from_file(self):
        freeze_file_name = os.path.join(self.temp_dir, 'frozen.txt')
        with open(freeze_file_name, 'w') as f:
            f.writelines([
                'a===1.0.0\n',
                'b===2.2.2\n',
            ])
        env = EnvPackages.from_freeze_file(freeze_file_name)
        packages = [p for p, _ in env]
        self.assertEqual(['a', 'b'], packages)

    def test_current_environment(self):
        env = EnvPackages.from_active_env()
        packages = [p for p, _ in env]
        # there will be more, but at least this will be included
        self.assertIn('PyYAML', packages)


class TestVirtualenv(unittest.TestCase):

    def test_bad_line(self):
        env = EnvPackages.from_freeze_file(
            StringIO('a===1.0.0\nxxx')
        )
        self.assertEqual(
            {'xxx'},
            env.packages_with_error
        )
        self.assertEqual('Could not parse package/version "xxx"\n', env.get_errors())
        packages = [p for p, _ in env]
        self.assertEqual(['a'], packages)
