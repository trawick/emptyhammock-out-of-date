import json
import os
import shutil
import tempfile
import unittest

import requests_mock

from e_ood.pypi import PackageVersionInfo


class Test(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, 'pypi_cache.json')
        self.test_package = '__foopkg__'  # not on PyPI, I hope

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @staticmethod
    def setup_response(m, package_name, versions):
        data = {
            'releases': {
                version: True
                for version in versions
            }
        }
        m.get(
            'https://pypi.python.org/pypi/%s/json' % package_name,
            text=json.dumps(data))

    @requests_mock.Mocker()
    def test_lookup(self, m):
        self.setup_response(m, self.test_package, ['1.0.1', '1.0.2', '1.0.3'])
        pvi = PackageVersionInfo(
            pypi_cache_file=self.cache_file
        )
        x = pvi.get(self.test_package)
        pvi.save()
        pvi = PackageVersionInfo(
            pypi_cache_file=self.cache_file
        )
        self.assertEqual({'1.0.1', '1.0.2', '1.0.3'}, set(x['releases'].keys()))
        # now it should be cached
        self.setup_response(m, self.test_package, ['2.0.1', '2.0.2', '2.0.3'])
        x = pvi.get(self.test_package)
        self.assertEqual({'1.0.1', '1.0.2', '1.0.3'}, set(x['releases'].keys()))

    @requests_mock.Mocker()
    def test_context_manager_normal_path(self, m):
        assert not os.path.exists(self.cache_file)
        self.setup_response(m, self.test_package, ['1.0.1', '1.0.2', '1.0.3'])
        with PackageVersionInfo(
            pypi_cache_file=self.cache_file
        ) as pvi:
            pvi.get(self.test_package)
        assert os.path.exists(self.cache_file)

    @requests_mock.Mocker()
    def test_context_manager_exception(self, m):
        assert not os.path.exists(self.cache_file)
        self.setup_response(m, self.test_package, ['1.0.1', '1.0.2', '1.0.3'])
        try:
            with PackageVersionInfo(
                pypi_cache_file=self.cache_file
            ) as pvi:
                pvi.get(self.test_package)
                raise RuntimeError("foo")
        except RuntimeError:
            pass
        assert not os.path.exists(self.cache_file)
