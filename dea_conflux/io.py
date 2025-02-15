"""Input/output for Conflux.

Matthew Alger
Geoscience Australia
2021
"""

import datetime
import json
import logging
import os
from pathlib import Path

import s3fs
import pandas as pd
import pyarrow
import pyarrow.parquet

logger = logging.getLogger(__name__)


# File extensions to recognise as Parquet files.
PARQUET_EXTENSIONS = {'.pq', '.parquet'}

# Metadata key for Parquet files.
PARQUET_META_KEY = 'conflux.metadata'.encode('ascii')

# Format of string date metadata.
DATE_FORMAT = '%Y%m%d-%H%M%S-%f'
DATE_FORMAT_DAY = '%Y%m%d'


def date_to_string(date: datetime.datetime) -> str:
    """Serialise a date.

    Arguments
    ---------
    date : datetime
    
    Returns
    -------
    str
    """
    return date.strftime(DATE_FORMAT)


def date_to_string_day(date: datetime.datetime) -> str:
    """Serialise a date discarding hours/mins/seconds.

    Arguments
    ---------
    date : datetime
    
    Returns
    -------
    str
    """
    return date.strftime(DATE_FORMAT_DAY)


def string_to_date(date: str) -> datetime.datetime:
    """Unserialise a date.

    Arguments
    ---------
    date : str
    
    Returns
    -------
    datetime
    """
    return datetime.datetime.strptime(date, DATE_FORMAT)


def make_name(
        drill_name: str,
        uuid: str,
        centre_date: datetime.datetime) -> str:
    """Make filename for Parquet.
    
    Arguments
    ---------
    drill_name : str
        Name of the drill.

    uuid : str
        UUID of reference dataset.
    
    centre_date : datetime
        Centre date of reference dataset.
    
    Returns
    -------
    str
        Parquet filename.
    """
    datestring = date_to_string(centre_date)
    return f'{drill_name}_{uuid}_{datestring}.pq'


def table_exists(
        drill_name: str, uuid: str,
        centre_date: datetime.datetime,
        output: str) -> bool:
    """Check whether a table already exists.

    Arguments
    ---------
    drill_name : str
        Name of the drill.

    uuid : str
        UUID of reference dataset.
    
    centre_date : datetime
        Centre date of reference dataset.
    
    table : pd.DataFrame
        Dataframe with index polygons and columns bands.
    
    output : str
        Path to output directory.
    
    Returns
    -------
    bool
    """
    name = make_name(drill_name, uuid, centre_date)
    foldername = date_to_string_day(centre_date)

    if not output.endswith('/'):
        output = output + '/'
    if not foldername.endswith('/'):
        foldername = foldername + '/'

    path = output + foldername + name

    if not output.startswith('s3://'):
        # local
        return os.path.exists(path)
    
    return s3fs.S3FileSystem().exists(path)


def write_table(
        drill_name: str, uuid: str,
        centre_date: datetime.datetime,
        table: pd.DataFrame, output: str):
    """Write a table to Parquet.
    
    Arguments
    ---------
    drill_name : str
        Name of the drill.

    uuid : str
        UUID of reference dataset.
    
    centre_date : datetime
        Centre date of reference dataset.
    
    table : pd.DataFrame
        Dataframe with index polygons and columns bands.
    
    output : str
        Path to output directory.
    """
    output = str(output)

    is_s3 = output.startswith('s3://')

    foldername = date_to_string_day(centre_date)

    if not is_s3:
        path = Path(output)
        os.makedirs(path / foldername, exist_ok=True)
    
    filename = make_name(drill_name, uuid, centre_date)

    # Convert the table to pyarrow.
    table_pa = pyarrow.Table.from_pandas(table)

    # Dump new metadata to JSON.
    meta_json = json.dumps({
        'drill': drill_name,
        'date': date_to_string(centre_date),
    })

    # Dump existing (Pandas) metadata.
    # https://towardsdatascience.com/
    #   saving-metadata-with-dataframes-71f51f558d8e
    existing_meta = table_pa.schema.metadata
    combined_meta = {
        PARQUET_META_KEY: meta_json.encode(),
        **existing_meta,
    }
    # Replace the metadata.
    table_pa = table_pa.replace_schema_metadata(combined_meta)

    # Write the table.
    if not output.endswith('/'):
        output = output + '/'
    
    if not foldername.endswith('/'):
        foldername = foldername + '/'

    pyarrow.parquet.write_table(
        table_pa,
        output + foldername + filename,
        compression='GZIP')


def read_table(path: str) -> pd.DataFrame:
    """Read a Parquet file with Conflux metadata.
    
    Arguments
    ---------
    path : str
        Path to Parquet file.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with attrs set.
    """
    table = pyarrow.parquet.read_table(path)
    df = table.to_pandas()
    meta_json = table.schema.metadata[PARQUET_META_KEY]
    metadata = json.loads(meta_json)
    for key, val in metadata.items():
        df.attrs[key] = val
    return df
