import json
import os
import time

import requests

import e_ood


class PackageVersionInfo(object):
    """
    Provide information about versions available on PyPI
    """

    def __init__(self, max_pypi_age_seconds=None):
        if max_pypi_age_seconds is None:
            max_pypi_age_seconds = 60 * 60 * 24
        user_path = os.path.expanduser('~')
        self.pyold_cache_file = os.path.join(user_path, '.pyold.json')
        try:
            self.pyold_cache = json.load(open(self.pyold_cache_file, 'r'))
        except:  # noqa
            self.pyold_cache = {}
        self.pyold_cache_changed = False
        request_headers = {
            'User-Agent': 'emptyhammock-ood %s' % e_ood.__version__,
        }
        self.max_pypi_age_seconds = max_pypi_age_seconds
        self.current_time_seconds = int(time.time())
        self.pypi_session = requests.Session()
        self.pypi_session.headers.update(request_headers)

    def save(self):
        if self.pyold_cache_changed:
            json.dump(self.pyold_cache, open(self.pyold_cache_file, 'w'))

    def get(self, package_name):

        if package_name in self.pyold_cache:
            retrieved = self.pyold_cache[package_name].get('retrieved')
            out_of_date = \
                (not retrieved) or \
                (retrieved < self.current_time_seconds - self.max_pypi_age_seconds)
            if out_of_date:
                del self.pyold_cache[package_name]
                self.pyold_cache_changed = True

        if package_name not in self.pyold_cache:
            url = 'https://pypi.python.org/pypi/%s/json' % package_name
            result = self.pypi_session.get(url)
            if result.status_code != 200:
                print('{} => {}'.format(url, result.status_code))
                return None
            self.pyold_cache[package_name] = {
                'from_pypi': json.loads(result.content.decode('utf-8')),
                'retrieved': self.current_time_seconds,
            }
            self.pyold_cache_changed = True

        return self.pyold_cache[package_name]['from_pypi']
