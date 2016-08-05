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
        yield l

if __name__ == '__main__':
  # Read in CSV report, strip the headers, blank lines
  csv = read_csv(args['from'])
  data = gen_csv(csv)

  # Make a renderable format

  for rec in data:
    rec_ = list(map(lambda n: n.strip(),rec.split(',')))
    print(rec_)

    # Aggregate the raw data
    # TAOTODO: