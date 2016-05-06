# -*- coding: utf-8 -*-
import dateparser
import datetime


def datetime_from_filename(filename):
    if all(filename[idx] == '-' for idx in (4, 7)):
        datestr = filename[0:10]
    else:
        return None
    if all(filename[idx] in ('-', ':') for idx in (13, 16)):
        timestr = filename[11:19].replace('-', ':')
    else:
        timestr = ''
    datetimestr = '{} {}'.format(datestr, timestr)
    return dateparser.parse(datetimestr)


def original_filename_from_filename(filename):
    # old format: 2016-05-03_00-02-59_A_G0070289.JPG
    # new format: 2016-05-03_00-02-59.A_G0070289.original.6c227c09a043c0e30a86a61ddd445734.JPG

    # remove the date and time
    filename = filename[20:]
    # remove '.' seperated stuff in the middle (size and checksum with new format)
    split = filename.split('.')
    filename = '{}.{}'.format(split[0], split[-1])
    return filename


def daterange(start_on, end_on):
    day_count = (end_on - start_on).days
    for day_num in range(0, day_count+1):
        yield start_on + datetime.timedelta(days=day_num)
