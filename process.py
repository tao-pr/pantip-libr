"""
Process the downloaded records in CouchDB

@starcolon projects
"""
from pydb import couch
from pprint import pprint
from termcolor import colored
from pypipe import pipe as Pipe
import subprocess
import json

def execute_background_services(commands):
	workers = []
	for cmd in commands:
		print(colored('🚀 Executing...','green') + cmd)
		sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		workers.append(sp)
	return workers

# Push the record through the processing pipeline
def push_pipeline(pipe):
	def go(rec):
		print(rec['title'])
		pass # TAOTODO: Trigger the pipe
	return go

def print_record(rec):
	print([rec['title'],rec['tags']])

if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Execute list of required background services
	services = ['ruby tokenizer/tokenizer.rb']
	workers  = execute_background_services(services)

	# Prepare the processing pipeline
	# TAOTODO:
	pipe = []

	# Iterate through each record and process
	couch.each_do(db,push_pipeline(pipe))

	# End of the process, terminate all background services
	print(colored('Ending workers...','cyan'))
	[w.kill() for w in workers]
