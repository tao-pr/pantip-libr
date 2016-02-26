"""
Process the downloaded records in CouchDB

@starcolon projects
"""
from pydb import couch
from pprint import pprint
from termcolor import colored
from pypipe import pipe as Pipe
import subprocess
import signal
import json
import os

def execute_background_services(commands):
	workers = []
	for cmd in commands:
		print(colored('🚀 Executing...','green') + cmd)
		sp = subprocess.Popen(cmd, 
			shell=True, stdout=subprocess.PIPE,
			preexec_fn=os.setsid)
		workers.append(sp.pid)
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

	# Kill all running background services before leaving
	print(colored('Ending background services...','green'))
	for pid in workers:
		subprocess.Popen('kill {0}'.format(pid), shell=True, stdout=subprocess.PIPE)
