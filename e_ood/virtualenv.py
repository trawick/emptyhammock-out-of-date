import io
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
        self.last_returned = -1

    def __iter__(self):
        """
        Does not support multiple simultaneous iterators!
        """
        self.last_returned = 0
        return self

    def __next__(self):
        if self.last_returned >= len(self.packages):
            raise StopIteration
        self.last_returned += 1
        return self.packages[self.last_returned - 1]

    def next(self):
        return self.__next__()

    def add(self, package_name, current_version):
        self.packages.append((package_name, current_version))

    def add_error_package(self, package_name, problem):
        self.packages_with_error.add(package_name)
        if self.verbose:
            print(problem)

    @staticmethod
    def get_process_output(process):
        if sys.version_info[0] == 2:
            while True:
                line = process.stdout.readline()
                if line == b'':
                    break
                yield line
        else:
            for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
                yield line

    @classmethod
    def _parse_package_list(cls, *args, **kwargs):
        lister = kwargs.pop('lister')
        env_packages = EnvPackages(*args, **kwargs)
        for line in lister():
            line = line.strip()
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
                env_packages.add_error_package(
                    package_name,
                    'Bad version "%s" for %s' % (current_version, package_name)
                )
        return env_packages

    @classmethod
    def from_active_env(cls, *args, **kwargs):
        process = Popen(['pip', 'freeze'], stdout=PIPE)

        def lister():
            for line in cls.get_process_output(process):
                yield line

        return cls._parse_package_list(*args, lister=lister, **kwargs)

    @classmethod
    def from_freeze_file(cls, freeze_file, *args, **kwargs):

        readlines = getattr(freeze_file, "readlines", None)
        if not callable(readlines):
            freeze_file = io.open(freeze_file, encoding='utf-8')

        def lister():
            for line in freeze_file.readlines():
                yield line

        try:
            return cls._parse_package_list(*args, lister=lister, **kwargs)
        finally:
            freeze_file.close()
