"""
Report charting renderer
@starcolon projects
"""

import sys
import pygal
import argparse
from termcolor import colored

arguments = argparse.ArgumentParser()
arguments.add_argument('--from', type=str, default='data/report.csv') # CSV file input of the report
arguments.add_argument('--to', type=str, default='data/') # Where to save graphical charts
args = vars(arguments.parse_args(sys.argv[1:]))

def read_csv(path):
  with open(path,'r') as csv:
    return csv.readlines()

def gen_csv(lines):
  header_found = False
  for l in lines:
    if not header_found:
      if 'CLUSTER' in l and 'DECOM' in l:
        header_found = True
    else:
      if len(l)>10:
        yield to_hash(l)

def to_hash(rec):
  rec = list(map(lambda n: n.strip(),rec.split(',')))
  return {
    'cluster': rec[0],
    'decom':   rec[1],
    'N':       int(rec[2]),
    'feat':    None if rec[3] == 'None' else int(rec[3]),
    'tag':     int(rec[4]),
    '#total':  float(rec[5]),
    '#0':      float(rec[6]),
    '#1':      float(rec[7]),
    '#-1':     float(rec[8])
  }

if __name__ == '__main__':
  # Read in CSV report, strip the headers, blank lines
  csv = read_csv(args['from'])
  data = gen_csv(csv)

  # Make a renderable format

  for rec in data:
    print(rec)

    # Aggregate the raw data
    # TAOTODO: