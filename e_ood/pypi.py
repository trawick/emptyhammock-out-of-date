""" Provide access to versions available in the package repository. """
import json
import logging
import os
import time

import requests

import e_ood


DEFAULT_LOGGER = logging.getLogger(__name__)


class PackageVersionInfo(object):
    """
    Provide information about versions available on PyPI
    """

    def __init__(self, max_pypi_age_seconds=None, pypi_cache_file=None, logger=None):
        self.logger = logger or DEFAULT_LOGGER

        if max_pypi_age_seconds is None:
            max_pypi_age_seconds = 60 * 60 * 24

        if pypi_cache_file is None:
            user_path = os.path.expanduser('~')
            self.pypi_cache_file = os.path.join(user_path, '.eood.json')
        else:
            self.pypi_cache_file = pypi_cache_file

        try:
            with open(self.pypi_cache_file, 'r') as cache_file:
                self.pypi_cache = json.load(cache_file)
        except IOError:
            # This might not simply be file-not-found.  Try to deal with the
            # different errors appropriately in a Py2/Py3 + lint-safe way.
            # For Python 3 only, just check for FileNotFoundError.
            if not os.path.exists(self.pypi_cache_file):
                self.pypi_cache = {}
            else:
                self.logger.exception('Could not read PyPI cache file "%s"', self.pypi_cache_file)
                raise
        except:  # noqa
            self.logger.exception('Could not parse PyPI cache file "%s"', self.pypi_cache_file)
            raise

        self.pypi_cache_changed = False
        request_headers = {
            'User-Agent': 'emptyhammock-ood %s' % e_ood.__version__,
        }
        self.max_pypi_age_seconds = max_pypi_age_seconds
        self.current_time_seconds = int(time.time())
        self.pypi_session = requests.Session()
        self.pypi_session.headers.update(request_headers)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.save()

    def save(self):
        """
        Save the PyPI cache if it was modified.

        This call is appropriate if you don't use the PackageVersionInfo
        context manager, which will call this method automatically.

        :return: nothing
        """
        if self.pypi_cache_changed:
            with open(self.pypi_cache_file, 'w') as cache_file:
                json.dump(self.pypi_cache, cache_file)

    def get(self, package_name):
        """
        Return PyPI data for the specified package.  It may come from the
        cache.

        :param package_name: name of package to look up
        :return: dictionary of data from PyPI
        """
        if package_name in self.pypi_cache:
            retrieved = self.pypi_cache[package_name].get('retrieved')
            out_of_date = \
                (not retrieved) or \
                (retrieved < self.current_time_seconds - self.max_pypi_age_seconds)
            if out_of_date:
                del self.pypi_cache[package_name]
                self.pypi_cache_changed = True

        if package_name not in self.pypi_cache:
            url = 'https://pypi.python.org/pypi/%s/json' % package_name
            result = self.pypi_session.get(url)
            if result.status_code not in (200, 404):
                self.logger.error(
                    'Received status code %s looking up package "%s"',
                    result.status_code, package_name
                )
                return None
            self.pypi_cache[package_name] = {
                'from_pypi':
                    json.loads(result.content.decode('utf-8'))
                    if result.status_code == 200 else None,
                'retrieved': self.current_time_seconds,
            }
            self.pypi_cache_changed = True

        return self.pypi_cache[package_name]['from_pypi']
