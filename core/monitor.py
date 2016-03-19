"""
Active topic analysis service
------------------------------
Keep the input MQ monitored all
the time, process and push the result
to the output MQ for another service 
to check out.

@starcolon projects
"""

from pydb import couch
from pprint import pprint
from queue import Queue
from termcolor import colored
from collections import deque
from pypipe import pipe as Pipe
from pypipe.operations import preprocess
from pypipe.operations import wordbag
from pypipe.operations import rabbit
import subprocess
import signal
import json
import time
import os

REPO_DIR = os.getenv('PANTIPLIBR','.')

def dequeue(feeder):
	pass

def process_text(text):
	pass

if __name__ == '__main__':

	# Startup message
	print(colored('--------------------------','cyan'))
	print(colored(' Analysis service started','cyan'))
	print(colored('--------------------------','cyan'))

	# Start the monitoring process
	mqinput = rabbit.create('localhost','')

