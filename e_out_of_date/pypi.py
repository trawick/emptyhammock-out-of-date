""" Provide information about versions available in the package repository. """
import json
import logging
import os
import time

import requests

import e_out_of_date


DEFAULT_LOGGER = logging.getLogger(__name__)


class AvailablePackageVersions(object):
    """
    Provide information about versions available on PyPI
    """

    def __init__(self, max_cache_time_seconds=None, cache_file_path=None, logger=None):
        self._logger = logger or DEFAULT_LOGGER

        if max_cache_time_seconds is None:
            max_cache_time_seconds = 60 * 60 * 24

        if cache_file_path is None:
            user_path = os.path.expanduser('~')
            self._cache_file_path = os.path.join(user_path, '.eood.json')
        else:
            self._cache_file_path = cache_file_path

        try:
            with open(self._cache_file_path, 'r') as cache_file:
                self._cache = json.load(cache_file)
        except IOError:
            # This might not simply be file-not-found.  Try to deal with the
            # different errors appropriately in a Py2/Py3 + lint-safe way.
            # For Python 3 only, just check for FileNotFoundError.
            if not os.path.exists(self._cache_file_path):
                self._cache = {}
            else:
                self._logger.exception('Could not read PyPI cache file "%s"', self._cache_file_path)
                raise
        except:  # noqa
            self._logger.exception('Could not parse PyPI cache file "%s"', self._cache_file_path)
            raise

        self._cache_modified = False
        request_headers = {
            'User-Agent': 'emptyhammock-ood %s' % e_out_of_date.__version__,
        }
        self._max_pypi_age_seconds = max_cache_time_seconds
        self._current_time_seconds = int(time.time())
        self._repo_session = requests.Session()
        self._repo_session.headers.update(request_headers)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.save()

    def save(self):
        """
        Save the PyPI cache if it was modified.

        This call is appropriate if you don't use the AvailablePackageVersions
        context manager, which will call this method automatically.

        :return: nothing
        """
        if self._cache_modified:
            with open(self._cache_file_path, 'w') as cache_file:
                json.dump(self._cache, cache_file)

    def get(self, package_name):
        """
        Return PyPI data for the specified package.  It may come from the
        cache.

        :param package_name: name of package to look up
        :return: dictionary of data from PyPI
        """
        if package_name in self._cache:
            retrieved = self._cache[package_name].get('retrieved')
            out_of_date = \
                (not retrieved) or \
                (retrieved < self._current_time_seconds - self._max_pypi_age_seconds)
            if out_of_date:
                del self._cache[package_name]
                self._cache_modified = True

        if package_name not in self._cache:
            url = 'https://pypi.python.org/pypi/%s/json' % package_name
            result = self._repo_session.get(url)
            if result.status_code not in (200, 404):
                self._logger.error(
                    'Received status code %s looking up package "%s"',
                    result.status_code, package_name
                )
                return None
            self._cache[package_name] = {
                'from_pypi':
                    json.loads(result.content.decode('utf-8'))
                    if result.status_code == 200 else None,
                'retrieved': self._current_time_seconds,
            }
            self._cache_modified = True

        return self._cache[package_name]['from_pypi']
