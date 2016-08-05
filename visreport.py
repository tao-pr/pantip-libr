"""
Report charting renderer
@starcolon projects
"""

import sys
import pygal
import argparse
from pygal import Config
from itertools import tee
from termcolor import colored
from pprint import pprint

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

def label(rec):
  return rec['cluster'].upper()

def param(rec):
  return rec['decom'] + '-' + str(rec['N'])

if __name__ == '__main__':
  # Read in CSV report, strip the headers, blank lines
  print(colored('Reading CSV report ...','cyan'))
  csv = read_csv(args['from'])
  data_1, data_2, data_3 = tee(gen_csv(csv),3)

  # Make a renderable chart
  # where the `decomposition algorithms` are plotted on X (corners of Radar)
  # and `variations of parameters` are plotted on Y (contour lines)
  print(colored('Preparing chart ...','cyan'))
  cfg      = Config()
  cfg.fill = True
  chart    = pygal.Radar(cfg)
  chart.title = 'Clustering/Feature Comparison'

  labels = list(set([label(n) for n in data_1]))
  chart.x_labels = labels

  params = list(set([param(n) for n in data_2]))

  # Aggregate chart input vectors
  chart_input = {par:[] for par in params}
  prev_label = None
  for d in data_3:
    lbl = label(d)
    par = param(d)
    chart_input[par].append(d['#total'])

  # Render now!
  print(colored('Drawing chart...','cyan'))
  for par,vec in chart_input.items():
    chart.add(par, vec)

  chart.render_to_file(args['to'] + '/radar.svg')
  print(colored('Done!','green'))
