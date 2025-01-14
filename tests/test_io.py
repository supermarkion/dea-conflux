import datetime
import logging
from pathlib import Path
import random
import sys

import pandas as pd
import pytest

import dea_conflux.io as io

logging.basicConfig(level=logging.INFO)

# Test directory.
HERE = Path(__file__).parent.resolve()

# Path to Canberra test shapefile.
TEST_SHP = HERE / 'data' / 'waterbodies_canberra.shp'

TEST_PLUGIN_OK = HERE / 'data' / 'sum_wet.conflux.py'
TEST_PLUGIN_COMBINED = HERE / 'data' / 'sum_pv_wet.conflux.py'
TEST_PLUGIN_MISSING_TRANSFORM = (
    HERE / 'data' / 'sum_wet_missing_transform.conflux.py')

TEST_WOFL_ID = '234fec8f-1de7-488a-a115-818ebd4bfec4'
TEST_FC_ID = '4d243358-152e-404c-bb65-7ea64b21ca38'


def setup_module(module):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger("").handlers = []


@pytest.fixture()
def conflux_table():
    return pd.DataFrame({
        'band1': [0, 1, 2],
        'band2': [5, 4, 3],
    }, index=['uid1', 'uid2', 'uid3'])


def test_write_table(conflux_table, tmp_path):
    test_date = datetime.datetime(2018, 1, 1)
    io.write_table('name', 'uuid', test_date,
                   conflux_table, tmp_path / 'outdir')
    outpath = (tmp_path / 'outdir' / '20180101' /
               'name_uuid_20180101-000000-000000.pq')
    assert outpath.exists()


def test_read_write_table(conflux_table, tmp_path):
    test_date = datetime.datetime(2018, 1, 1)
    io.write_table('name', 'uuid', test_date,
                   conflux_table, tmp_path / 'outdir')
    outpath = (tmp_path / 'outdir' / '20180101' /
               'name_uuid_20180101-000000-000000.pq')
    table = io.read_table(outpath)
    assert len(table) == 3
    assert len(table.columns) == 2
    assert table.attrs['date'] == '20180101-000000-000000'
    assert table.attrs['drill'] == 'name'


def test_string_date():
    random.seed(0)
    for _ in range(100):
        d = random.randrange(1, 1628000000)  # from the beginning of time...
        d = datetime.datetime.fromtimestamp(d)
        assert io.string_to_date(io.date_to_string(d)) == d
