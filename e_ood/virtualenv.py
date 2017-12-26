import io
from subprocess import Popen, PIPE
import sys

from pkg_resources import parse_version


class EnvPackages(object):
    """
        Grok the packages/versions in the virtualenv and track any problems
        retrieving or understanding their versions.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.packages = []
        self.packages_with_error = set()
        self.last_returned = -1

    def __iter__(self):
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
    def from_active_env(cls, *args, **kwargs):
        env_packages = EnvPackages(*args, **kwargs)
        process = Popen(['pip', 'freeze'], stdout=PIPE)
        for line in cls.get_process_output(process):
            line = line.rstrip()
            package_name, current_version = line.split('==')
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
    def from_freeze_file(cls, freeze_file, *args, **kwargs):
        env_packages = EnvPackages(*args, **kwargs)
        for line in io.open(freeze_file, encoding='utf-8').readlines():
            line = line.rstrip()
            package_name, current_version = line.split('==')
            try:
                current_version = parse_version(current_version)
                env_packages.add(package_name, current_version)
            except ValueError:
                env_packages.add_error_package(
                    package_name,
                    'Bad version "%s" for %s' % (current_version, package_name)
                )
        return env_packages
