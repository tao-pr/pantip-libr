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


REPO_DIR = os.getenv('PANTIPLIBR','.')

def next_queue_please(feeder):
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
	print(colored('--------------------------','yellow'))
	print(colored(' Signaled to terminate...','yellow'))
	print(colored('--------------------------','yellow'))
	sys.exit(0)

if __name__ == '__main__':

	# Startup message
	print(colored('--------------------------','cyan'))
	print(colored(' Analysis service started','cyan'))
	print(colored('--------------------------','cyan'))

	# Start the monitoring process
	mqinput = rabbit.create('localhost','for-process')


	# Await ...
	signal.signal(signal.SIGINT, on_signal)
	signal.pause()
