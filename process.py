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
from pypipe.operations import hasher
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
	services = ['ruby tokenizer/tokenizer.rb']
	workers  = execute_background_services(services)

	# Delayed start
	time.sleep(2)

	# Prepare resources
	mq_raw      = rabbit.create('localhost','pantipsrc')
	mq_vector   = rabbit.create('localhost','pantipvec')
	transformer = hasher.safe_load('./data/transformer/00')

	# Prepare the processing pipeline (order matters)
	pipe      = Pipe.new('preprocess',[])
	Pipe.push(pipe,preprocess.take)
	Pipe.push(pipe,rabbit.feed(mq_raw))
	Pipe.then(pipe,lambda out: print(colored('[DONE!]','cyan')))

	# Iterate through each record and process
	couch.each_do(db,process_with(pipe),limit=3)

	# Save the transformer objects
	hasher.save(transformer,'./data/transformer/00')

	# Disconnect from the MQs
	rabbit.end(mq_raw)

	# End all background services
	terminate_background_services(workers)

