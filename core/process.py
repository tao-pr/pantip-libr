"""
Process the downloaded Pantip threads

@starcolon projects
"""
from pydb import couch
from pprint import pprint
from termcolor import colored
from pypipe import pipe as Pipe
from pypipe.operations import preprocess
from pypipe.operations import rabbit
import subprocess
import signal
import json
import time
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

def terminate_background_services(workser):
	# Kill all running background services before leaving
	print(colored('Ending background services...','green'))
	for pid in workers:
		subprocess.Popen('kill {0}'.format(pid), 
			shell=True, stdout=subprocess.PIPE)

def print_record(rec):
	print([rec['title'],rec['tags']])

# Couple the processing pipe with the input
def process_with(pipe):
	def f(input0):
		Pipe.operate(pipe,input0)
	return f


if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Execute list of required background services
	services = [
		'ruby core/tokenizer/tokenizer.rb'
		###'python3 core/textprocess.py' TAOTODO:Resurrect this script
		]
	workers  = execute_background_services(services)

	# Delayed start
	time.sleep(2)

	# Prepare resources
	mq          = rabbit.create('localhost','pantipsrc')

	# Prepare the processing pipeline (order matters)
	pipe      = Pipe.new('preprocess',[])
	Pipe.push(pipe,preprocess.take)
	Pipe.push(pipe,rabbit.feed(mq))
	Pipe.then(pipe,lambda out: print(colored('[DONE!]','cyan')))

	# Iterate through each record and process
	couch.each_do(db,process_with(pipe),limit=3)

	# Disconnect from the MQs
	rabbit.end(mq)

	# TAOTODO: End the process until we see the finishing signal
	# from the child processes

	# End all background services
	terminate_background_services(workers)

