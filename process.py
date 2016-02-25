"""
Process the downloaded records in CouchDB

@starcolon projects
"""
from pydb import couch
from pprint import pprint
from termcolor import colored
import json

def make_data_row(rec):
	print([rec['title'],rec['tags']])

if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Iterate through each record and process
	couch.each_do(db,make_data_row)