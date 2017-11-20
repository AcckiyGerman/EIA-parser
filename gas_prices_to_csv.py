#!/usr/bin/env python3

import requests
import csv
import json
from pprint import pprint
from datetime import datetime
import os

API_URL = 'http://api.eia.gov/series/'
API_KEY = '9934a8936353e7896834e2a4c211c360'
series_id = 'NG.RNGWHHD.D'


def get_data(start_date='19970101', end_date='20991231'):
    """
    Fetch records from the API for the given period of time.
    :param start_date: 'YYYYMMDD'
    :param end_date: 'YYYYMMDD'
    :return: {
        'data': [ [date, price], [date, price], ... ],
        'meta': {all other data from series}
    }
    :return: string: raw text data
    """
    # see the request and response format at
    # https://www.eia.gov/opendata/commands.php
    response = requests.get(url=API_URL, params={
        'api_key': API_KEY,
        'series_id': series_id,
        'out': 'json',
        'start': start_date,
        'end': end_date
    })

    return response.text


def write_csv(filename, data, header=''):
    """
    Creates the csv file with the data.
    :param filename: name of the file
    :param data: list of records
    :param header: header to be written to a file
    """
    with open(filename, 'w') as file:
        if header:
            file.write(header+'\n')
        writer = csv.writer(file)
        for record in data:
            writer.writerow(record)


def split_monthly(data):
    """
    Separates all records monthly.
    :param data: list of records
    :return: dict where keys are 'YYYYMM' and each value is a list of records.
        Example: {
                '200102': [ ['20010201', '5.5'], ['20010202', '5.6'],
                '200103': [...],
                ...
            }
    """
    separated_records = dict()
    for record in data:
        yyyymm = record[0][:6]  # '199701'
        if yyyymm in separated_records.keys():
            separated_records[yyyymm].append(record)
        else:
            separated_records[yyyymm] = [record]
    return separated_records


def create_data_package(data, meta):
    """
    1. Creates 'data' folder
    2. Saves given data into csv files (one file for each month)
    3. Creates and fills the 'datapackage.json'
    :param: data: [ [date, price], [date, price], ... ],
    :param: meta: {all other data from series}
    """
    # check|create the 'data' folder
    if not os.path.exists('data'):
        os.makedirs('data')

    # save csv files, form 'resources' list
    resources = list()
    for YYYYMM, month_records in split_monthly(data).items():
        month_records.sort(key=lambda record: record[0])  # sort by date
        filename = 'data/%s.csv' % YYYYMM
        write_csv(filename, month_records, header='date, price')
        # create record about this file for including into datapackage.json
        resources.append({
            'name': 'Gas prices in %s %s' % (YYYYMM[0:4], YYYYMM[4:6]),
            'path': filename,
            'format': 'csv',
            'mediatype': 'text/csv',
            'schema': {
                'fields': [
                    {
                        'name': 'date',
                        'type': 'string'
                    },
                    {
                        'name': 'price',
                        'type': 'number',
                    }
                ]
            }
        })

    meta['resources'] = resources
    # save datapackage.json file
    with open('data/datapackage.json', 'w') as file:
        pprint(meta, stream=file)


if __name__ == '__main__':
    now = datetime.now()
    current_date = '%d%2d%2d' % (now.year, now.month, now.day)
    raw_json = get_data(end_date=current_date)
    # extract data
    series = json.loads(raw_json)['series'][0]
    records = series['data']
    # clean data to get metadata
    del series['data']
    create_data_package(data=records, meta=series)
