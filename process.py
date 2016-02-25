"""
Process the downloaded records in CouchDB

@starcolon projects
"""
from pydb import couch
from pprint import pprint
from termcolor import colored
from pypipe import pipe as Pipe
import json

# Push the record through the processing pipeline
def push_pipeline(pipe):
	def go(rec):
		pass # TAOTODO: Trigger the pipe
	return go

def print_record(rec):
	print([rec['title'],rec['tags']])

if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Prepare the processing pipeline
	# TAOTODO:
	pipe = []

	# Iterate through each record and process
	couch.each_do(db,make_data_row(pipe))