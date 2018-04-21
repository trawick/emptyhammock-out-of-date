from pkg_resources import parse_version

from .db import ReportedUpdateTypes


class AnalyzerPackageReport(object):

    def __init__(self, version_db, package_name, current_version):
        self.version_db = version_db
        self.name = package_name
        self.current_version = current_version
        self.ignored = False
        self.no_version_info = False
        self.up_to_date = False
        self.newer = []
        self.older = []
        self.bad_versions = []

    def render_to_list(self, verbose=False):
        messages = []

        if self.newer:
            messages.append('%s: %s' % (self.name, self.current_version))
            newer = [
                str(v)
                for v in sorted(self.newer)
            ]

            messages.append('Newer releases:')
            for n in newer:
                messages.append('  %s: %s' % (n, self.version_db.classify_release(self.name, n)))
            changelog = self.version_db.get_changelog(self.name)
            if changelog:
                messages.append('  Changelog: %s' % changelog)

        if verbose and self.older:
            if not self.newer:
                messages.append('%s: %s' % (self.name, self.current_version))
            older = [
                str(v)
                for v in sorted(self.older)
            ]
            messages.append('Older: %s' % ', '.join(older))
        if self.newer or (verbose and self.older):
            messages.append('')

        return messages


class AnalyzerReport(object):

    def __init__(self, version_db):
        self.packages = []
        self.version_db = version_db

    def add_package(self, package_name, current_version):
        pr = AnalyzerPackageReport(self.version_db, package_name, current_version)
        self.packages.append(pr)
        return pr

    def render(self, verbose=False):
        messages = []
        up_to_date = []
        no_version_info = []
        for package in self.packages:
            messages += package.render_to_list(verbose)
            if package.up_to_date:
                up_to_date.append(package.name)
            if package.no_version_info:
                no_version_info.append(package.name)
        if up_to_date:
            messages.append('Up to date: %s\n' % ', '.join(up_to_date))
        if no_version_info:
            messages.append(
                'Packages with PyPI or version problem: %s\n' % ', '.join(
                    sorted(no_version_info)
                )
            )

        return '\n'.join(messages)


class Analyzer(object):

    def __init__(self, env, version_info, version_db):
        self.verbose = False
        self.env = env
        self.version_info = version_info
        self.version_db = version_db
        self.up_to_date = []

    def analyze(self, ignored_packages=None, types=None):
        ignored_packages = ignored_packages or []
        types = types or ReportedUpdateTypes()
        report = AnalyzerReport(self.version_db)
        self.up_to_date = []
        for package_name, current_version in self.env:
            current_version_str = str(current_version).lstrip('=')
            p_report = report.add_package(package_name, current_version_str)
            if package_name in ignored_packages:
                p_report.ignored = True
                continue
            data = self.version_info.get(package_name)
            if data is None:
                p_report.no_version_info = True
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
                        p_report.older.append(pypi_release)
                        older.append(pypi_release)
                except:  # noqa
                    # currently unreachable, as we allow parse_version() to return
                    # a LegacyVersion
                    p_report.bad_versions.append(str(pypi_release))
                    self.env.add_error_package(
                        package_name,
                        'Bad version "{}" for {}'.format(pypi_release, package_name)
                    )
            current_version = current_version_str
            try:
                newer = self.version_db.filter_available_releases(
                    package_name, current_version, newer, types,
                )
                for n in newer:
                    p_report.newer.append(n)
            except ValueError:
                # The lack of an entry for the package will show up later, if there
                # are indeed newer versions.
                pass
            if not newer:
                p_report.up_to_date = True
                self.up_to_date.append(package_name)

        return report
