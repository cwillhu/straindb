''' File I/O functions '''

import csv

def get_reader(csvfile_obj):  # csvfile_obj is file object returned by open()
    return ( csv.reader(csvfile_obj, delimiter=',', quotechar='"') )


def get_writer(csvfile_obj):  # csvfile_obj is file object returned by open()
    return( csv.writer(csvfile_obj, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL) )


def read_header(csvfile):  # csvfile is a Path object
    f = open(csvfile, 'r')
    reader = get_reader(f)
    return( next(reader) )


def write_header(csvfile, row):  # csvfile is a Path object
    csvfile.parent.mkdir(parents=True, exist_ok=True)
    with open(csvfile, 'w') as f:
        writer = get_writer(f)
        writer.writerow(row)

def mkparent(fyle):  # fyle is a Path object
    fyle.parent.mkdir(parents=True, exist_ok=True)
