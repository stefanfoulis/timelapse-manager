# -*- coding: utf-8 -*-
import dateparser


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
