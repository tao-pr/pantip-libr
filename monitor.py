"""
Active topic analysis service
------------------------------
Keep the input MQ monitored all
the time, process and push the result
to the output MQ for another service 
to check out.

@starcolon projects
"""

from termcolor import colored
from pprint import pprint
from queue import Queue
from collections import deque
from core.pydb import couch
from core.pypipe import pipe as Pipe
from core.pypipe.operations import preprocess
from core.pypipe.operations import wordbag
from core.pypipe.operations import rabbit
import subprocess
import signal
import json
import time
import sys
import os


workers  = []
REPO_DIR = os.getenv('PANTIPLIBR','.')

def execute_background_services():
	global workers
	services = ['ruby {0}/core/tokenizer/tokenizer.rb'.format(REPO_DIR)]

	workers = []
	for s in services:
		print('Executing: {0}'.format(s))
		sp = subprocess.Popen(
			s,
			shell=True,
			stdout=subprocess.PIPE,
			preexec_fn=os.setsid
		)
		workers.append(sp)

	return workers

def next_queue_please(feeder):
	# Take the input message out of the MQ
	# TAOTODO: this should be a consumer model 
	# (non-blocking)

	msg = rabbit.iter(feeder)

	# Tokenise the message
	_msg = preprocess.take(msg)

	# Feed the tokenised message 
	# to the classification process
	# TAOTODO:


	pass

def process_text(text):
	# Push the text to process
	feeder = rabbit.create('localhost','mqinput')
	pass

def publish_output(feeders,messageid,output):
	feed = rabbit.feed([feeders])
	pack = {
		id: messageid,
		out: output
	}
	feed(pack)

def on_signal(signal,frame):
	global workers
	print(colored('--------------------------','yellow'))
	print(colored(' Signaled to terminate...','yellow'))
	print(colored('--------------------------','yellow'))

	# End all background services
	for sp in workers:
		subprocess.Popen(
			'kill {0}'.format(sp.pid),
			shell=True, 
			stdout=subprocess.PIPE
		)	

	# Keep waiting until all subprocess were killed
	print('Waiting for services to end...')
	[sp.wait() for sp in workers]

	sys.exit(0)

if __name__ == '__main__':

	# Startup message
	print(colored('--------------------------','cyan'))
	print(colored(' Analysis service started','cyan'))
	print(colored('--------------------------','cyan'))

	# Start the monitoring process
	mqinput = rabbit.create('localhost','for-process')

	# Execute all background services
	workers = execute_background_services()


	# Await ...
	signal.signal(signal.SIGINT, on_signal)
	signal.pause()
