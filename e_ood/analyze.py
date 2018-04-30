from pkg_resources import parse_version

from .db import ReportedUpdateTypes


class AnalyzerPackageReport(object):

    def __init__(self, version_db, package_name, current_version):
        self.version_db = version_db
        self.name = package_name
        self.current_version = current_version
        self.no_version_info = False
        self.up_to_date = False
        self.newer = []
        self.older = []
        self.bad_versions = []

    def __str__(self):
        return 'Report for "%s"' % self.name

    def render_to_list(self, verbose=False):
        messages = []

        if self.newer:
            messages.append('%s: %s' % (self.name, self.current_version))
            newer = [
                str(v)
                for v in sorted(self.newer)
            ]

            messages.append('Newer releases:')
            for release in newer:
                messages.append('  %s: %s' % (
                    release, self.version_db.classify_release(self.name, release)
                ))
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
        render_all = verbose
        for package in self.packages:
            messages += package.render_to_list(verbose)
            if package.newer:
                render_all = True
            if package.up_to_date:
                up_to_date.append(package.name)
            if package.no_version_info:
                render_all = True
                no_version_info.append(package.name)

        if render_all and up_to_date:
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
            if package_name in ignored_packages:
                continue
            p_report = report.add_package(package_name, current_version_str)
            data = self.version_info.get(package_name)
            if data is None:
                p_report.no_version_info = True
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
            current_version = current_version_str
            try:
                newer = self.version_db.filter_available_releases(
                    package_name, current_version, newer, types,
                )
            except ValueError:  # this package doesn't appear in page release database
                # all newer releases will be reported, since the package release
                # database can't filter out any
                pass
            for n in newer:
                p_report.newer.append(n)
            if not newer:
                p_report.up_to_date = True
                self.up_to_date.append(package_name)

        return report
