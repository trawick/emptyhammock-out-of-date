import json
import logging
import os
import time

import requests

import e_ood


logger = logging.getLogger(__name__)


class PackageVersionInfo(object):
    """
    Provide information about versions available on PyPI
    """

    def __init__(self, max_pypi_age_seconds=None, pypi_cache_file=None):
        if max_pypi_age_seconds is None:
            max_pypi_age_seconds = 60 * 60 * 24

        if pypi_cache_file is None:
            user_path = os.path.expanduser('~')
            self.pypi_cache_file = os.path.join(user_path, '.eood.json')
        else:
            self.pypi_cache_file = pypi_cache_file

        try:
            with open(self.pypi_cache_file, 'r') as f:
                self.pypi_cache = json.load(f)
        except:  # noqa
            self.pypi_cache = {}

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
        if self.pypi_cache_changed:
            with open(self.pypi_cache_file, 'w') as f:
                json.dump(self.pypi_cache, f)

    def get(self, package_name):
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
                logger.error(
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
