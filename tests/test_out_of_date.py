from contextlib import contextmanager
import os
import shutil
import sys
import tempfile
import unittest

from six import StringIO

from e_ood.command import main

PY2 = sys.version_info[0] == 2


# https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestImplementation(unittest.TestCase):
    """ Test the core of the command-line tool, which exists in a library """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.freeze_file = os.path.join(self.temp_dir, 'pip_freeze.out')
        if PY2:
            self.assertRegex = self.assertRegexpMatches

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_bad_types_arg(self):
        with captured_output() as (out, err):
            with self.assertRaises(SystemExit) as exit_exception:
                main([
                    '--types',
                    'foobar',
                ])
        self.assertEqual(1, exit_exception.exception.code)
        self.assertEqual('', out.getvalue())
        self.assertEqual('Bad value for --types', err.getvalue().strip())

    def test_packages_with_error(self):
        with open(self.freeze_file, 'w') as freeze:
            freeze.write('foobar\n')
        with captured_output() as (out, err):
            main([
                self.freeze_file
            ])
        self.assertEqual('', out.getvalue())
        self.assertRegex(
            err.getvalue().replace('\n', ' '), r'with error:.*foobar'
        )
