""" Analyze contents of virtualenv with respect to newer available package versions """
from pkg_resources import parse_version

from .db import ReportedUpdateTypes


class AnalyzerPackageReport(object):
    """
    Report created for a particular package within the virtualenv being analyzed
    """

    def __init__(self, package_name, current_version):
        self.name = package_name
        self.current_version = current_version
        self.no_version_info = False
        self.up_to_date = False
        self.newer = []
        self.older = []
        self.bad_versions = []

    def __str__(self):
        return 'Report for "%s"' % self.name

    def render(self, version_db, verbose=False):
        """
        Render this report (info on a particular package) to a string.

        :param version_db: PackageVersionClassifications object, for classifying releases
        :param verbose: Include more than minimal information in the report
        :return: the rendered report, in the form of a string
        """
        return '\n'.join(self.render_to_list(version_db, verbose))

    def render_to_list(self, version_db, verbose=False):
        """
        Render this report (info on a particular package) to a list of strings,
        for easy consolidation into a report on the entire virtualenv.

        :param version_db: PackageVersionClassifications object, for classifying releases
        :param verbose: Include more than minimal information in the report
        :return: the rendered report, in the form of a list of strings
        """
        messages = []

        def _header():
            if not messages:
                messages.append('%s: %s' % (self.name, self.current_version))

        def _footer():
            if messages:
                messages.append('')

        if self.newer:
            _header()
            newer = [
                str(v)
                for v in sorted(self.newer)
            ]

            messages.append('Newer releases:')
            for release in newer:
                messages.append('  %s: %s' % (
                    release, version_db.classify_release(self.name, release)
                ))
            changelog = version_db.get_changelog(self.name)
            if changelog:
                messages.append('  Changelog: %s' % changelog)

        if self.bad_versions:
            _header()
            messages.append('Unparsable versions on PyPI: %s' % ', '.join(self.bad_versions))

        if verbose and self.older:
            _header()
            older = [
                str(v)
                for v in sorted(self.older)
            ]
            messages.append('Older: %s' % ', '.join(older))

        _footer()

        return messages


class AnalyzerReport(object):
    """
    Report created for the virtualenv being analyzed; this is the type of
    object returned from Analyzer.analyze().
    """

    def __init__(self, version_db):
        self.packages = []
        self.version_db = version_db

    def add_package(self, package_name, current_version):
        """
        Add another package to the report
        :param package_name: name of package
        :param current_version: current version of the package in the
            virtualenv
        :return: new instance of AnalyzerPackageReport representing the
            analysis of that package
        """
        package_report = AnalyzerPackageReport(package_name, current_version)
        self.packages.append(package_report)
        return package_report

    def render(self, verbose=False):
        """
        Create a printable report of the analysis results
        :param verbose: Include more than minimal information in the report
        :return: report string
        """
        messages = []
        up_to_date = []
        no_version_info = []
        render_all = verbose
        for package in self.packages:
            messages += package.render_to_list(self.version_db, verbose)
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


class Analyzer(object):  # pylint: disable=too-few-public-methods
    """
    Analyze a virtualenv based on current package versions, newer versions
    available from PyPI, and a categorization of those packages.
    """

    def __init__(self, env, version_info, version_db):
        self.env = env
        self.version_info = version_info
        self.version_db = version_db
        self.up_to_date = []

    def _report_newer_versions_of_interest(
            self, p_report, current_version, newer, types
    ):
        try:
            newer = self.version_db.filter_available_releases(
                p_report.name, current_version, newer, types,
            )
        except ValueError:  # this package doesn't appear in page release database
            # all newer releases will be reported, since the package release
            # database can't filter out any
            pass
        for version in newer:
            p_report.newer.append(version)
        if not newer:
            p_report.up_to_date = True
            self.up_to_date.append(p_report.name)

    def analyze(self, ignored_packages=None, types=None):
        """
        Analyze the virtualenv, and return an AnalyzerReport.

        :param ignored_packages: iterable of names of packages that won't be
            analyzed
        :param types: ReportedUpdateTypes instance, to decide which types of
            newer package versions are of interest
        :return: AnalyzerReport
        """
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
            for pypi_release in data['releases'].keys():
                # Add a tiny requirement on the format of the release strings.
                # parse_version() doesn't care about the format, and will
                # return LegacyVersion for any sort of contents.  We need to
                # be able to compare versions to find newer ones.
                if not pypi_release[0].isdigit():
                    p_report.bad_versions.append(str(pypi_release))
                    continue
                pypi_release = parse_version(pypi_release)
                if pypi_release > current_version:
                    newer.append(pypi_release)
                elif pypi_release != current_version:
                    p_report.older.append(pypi_release)

            self._report_newer_versions_of_interest(
                p_report, current_version_str, newer, types
            )

        return report
