# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os

import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from i18naddress.downloader import download


@pytest.fixture(autouse=True)
def patch_i18n_country_data(monkeypatch, tmpdir):
    manager_dict = {'PL': 'datą', 'US': 'data'}
    all_countries = ['PL', 'US']
    data_dir = tmpdir.join('data')
    monkeypatch.setattr('i18naddress.downloader.ThreadPool', mock.MagicMock())
    monkeypatch.setattr('i18naddress.downloader.work_queue', mock.MagicMock())
    monkeypatch.setattr('i18naddress.downloader.get_countries', lambda: all_countries)
    monkeypatch.setattr(
        'i18naddress.downloader.COUNTRIES_VALIDATION_DATA_DIR', str(data_dir))
    monkeypatch.setattr(
        'i18naddress.downloader.COUNTRY_PATH', os.path.join(str(data_dir), '%s.json'))
    manager = mock.MagicMock()
    manager.dict.return_value = manager_dict
    monkeypatch.setattr('i18naddress.downloader.manager', manager)


@pytest.mark.parametrize('country, file_names, data', [
    (None, ('pl.json', 'us.json', 'all.json'), {
        'pl.json': {'PL': 'datą'},
        'us.json': {'US': 'data'},
        'all.json': {'PL': 'datą', 'US': 'data'}}),
    ('PL', ('pl.json', 'all.json'), {
        'pl.json': {'PL': 'datą'},
        'all.json': {'PL': 'datą'}}
     ),
    pytest.mark.xfail((None, ('de.json',), None), raises=AssertionError),
    pytest.mark.xfail(('PL', ('us.json',), None), raises=AssertionError)
])
def test_downloader_invalid_country(tmpdir, country, file_names, data):
    data_dir = tmpdir.join('data')
    download(country)
    for file_name in file_names:
        assert data_dir.join(file_name).exists()
        assert json.load(data_dir.join(file_name)) == data[file_name]