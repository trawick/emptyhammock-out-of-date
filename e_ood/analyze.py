from pkg_resources import parse_version

from .db import ReportedUpdateTypes


class Analyzer(object):

    def __init__(self, env, version_info, version_db):
        self.verbose = False
        self.env = env
        self.version_info = version_info
        self.version_db = version_db
        self.up_to_date = []
        self.messages = []

    def analyze(self, ignored_packages=None, types=None):
        ignored_packages = ignored_packages or []
        types = types or ReportedUpdateTypes()
        self.up_to_date = []
        for package_name, current_version in self.env:
            if package_name in ignored_packages:
                continue
            data = self.version_info.get(package_name)
            if data is None:
                self.env.add_error_package(package_name, 'No version information found')
                continue
            newer = []
            older = []
            for pypi_release in data['releases'].keys():
                try:
                    pypi_release = parse_version(pypi_release)
                    if pypi_release > current_version:
                        newer.append(pypi_release)
                    elif pypi_release != current_version:
                        older.append(pypi_release)
                except:  # noqa
                    self.env.add_error_package(
                        package_name,
                        'Bad version "{}" for {}'.format(pypi_release, package_name)
                    )
            current_version = str(current_version).lstrip('=')
            try:
                newer = self.version_db.filter_available_releases(
                    package_name, current_version, newer, types,
                )
            except ValueError:
                # The lack of an entry for the package will show up later, if there
                # are indeed newer versions.
                pass
            if newer:
                self.messages.append('%s: %s' % (package_name, current_version))
                newer = [
                    str(v)
                    for v in sorted(newer)
                ]
                self.messages.append('Newer releases:')
                for n in newer:
                    self.messages.append('  %s: %s' % (n, self.version_db.classify_release(package_name, n)))
                changelog = self.version_db.get_changelog(package_name)
                if changelog:
                    self.messages.append('  Changelog: %s' % changelog)
            else:
                self.up_to_date.append(package_name)
            if self.verbose and older:
                if not newer:
                    self.messages.append('%s: %s' % (package_name, current_version))
                older = [
                    str(v)
                    for v in sorted(older)
                ]
                self.messages.append('Older: %s' % ', '.join(older))
            if newer or (self.verbose and older):
                self.messages.append('')

        return '\n'.join(self.messages)
