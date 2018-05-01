"""Represent contents of virtualenv"""
import io
import re
from subprocess import Popen, PIPE
import sys

from pkg_resources import parse_version


class EnvPackages(object):
    """
        Grok the packages/versions in the virtualenv and track any problems
        retrieving or understanding their versions.

        Use .from_active_env() or .from_freeze_file() to create an
        instance.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.packages = []
        self.packages_with_error = set()
        self.error_messages = []

    def get_errors(self):
        """
        Get printable output representing all the errors encountered while
        parsing the packages/versions in the virtualenv.
        :return: report string
        """
        return '\n'.join(self.error_messages) + ('\n' if self.error_messages else '')

    def __iter__(self):
        return EnvPackagesIterator(self.packages)

    def add(self, package_name, current_version):
        self.packages.append((package_name, current_version))

    def add_error_package(self, package_name, problem):
        self.packages_with_error.add(package_name)
        self.error_messages.append(problem)
        if self.verbose:
            print(problem)

    @staticmethod
    def _get_process_output(process):
        if sys.version_info[0] == 2:
            while True:
                line = process.stdout.readline()
                if line == b'':
                    break
                yield line
        else:
            with io.TextIOWrapper(process.stdout, encoding="utf-8") as output:
                for line in output:
                    yield line

    @classmethod
    def _parse_package_list(cls, *args, **kwargs):
        lister = kwargs.pop('lister')
        env_packages = EnvPackages(*args, **kwargs)
        for line in lister():
            try:
                package_name, current_version = line.split('==')
            except ValueError:
                env_packages.add_error_package(
                    line,
                    'Could not parse package/version "%s"' % line,
                )
                continue
            try:
                current_version = parse_version(current_version)
                env_packages.add(package_name, current_version)
            except ValueError:
                # unreachable, as parse_version() will create a LegacyVersion
                # with any sort of junk for the string
                env_packages.add_error_package(
                    package_name,
                    'Bad version "%s" for %s' % (current_version, package_name)
                )
        return env_packages

    @classmethod
    def from_active_env(cls, *args, **kwargs):
        """
        Create EnvPackages object representing the current virtualenv.

        :param args: passed to EnvPackages constructor
        :param kwargs: passed to EnvPackages constructor
        :return: new EnvPackages object
        """
        process = Popen(['pip', 'freeze'], stdout=PIPE)

        def lister():
            """Helper function for reading from the current virtualenv"""
            for line in cls._get_process_output(process):
                yield line.strip()
            process.terminate()

        return cls._parse_package_list(*args, lister=lister, **kwargs)

    @classmethod
    def from_freeze_file(cls, freeze_file, *args, **kwargs):
        """
        Create EnvPackages object representing the virtualenv whose contents
        were captured to the specified file (presumably via "pip freeze").

        :param freeze_file: Path name to file or file-like object from which
            "pip freeze" output may be read
        :param args: passed to EnvPackages constructor
        :param kwargs: passed to EnvPackages constructor
        :return: new EnvPackages object
        """
        readlines = getattr(freeze_file, "readlines", None)
        if not callable(readlines):
            freeze_file = io.open(freeze_file, encoding='utf-8')

        def lister():
            """Helper function for reading from freeze files"""
            for line in freeze_file.readlines():
                line = line.strip()
                if re.search(r'^(#|$)', line):
                    continue
                yield line

        try:
            return cls._parse_package_list(*args, lister=lister, **kwargs)
        finally:
            freeze_file.close()


class EnvPackagesIterator(object):
    """Python iterator object for EnvPackages class"""

    def __init__(self, packages):
        self.packages = packages
        self.index = 0

    def __next__(self):
        """Part of Python 3 iterator protocol """
        try:
            package = self.packages[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return package

    def next(self):
        """Part of Python 2 iterator protocol """
        return self.__next__()

    def __iter__(self):
        """Part of iterator protocol"""
        return self
