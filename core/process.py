"""
Process the downloaded Pantip threads
------------------------------------
The script tokenises each of the records 
in CouchDB, and pass it as a series of input 
to train the classificier(s).

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
WORD_BAG_DIR = '{0}/data/words/freq.txt'.format(REPO_DIR)

def execute_background_services(commands):
	workers = []
	for cmd in commands:
		print(colored('🚀 Executing...','green') + cmd)
		sp = subprocess.Popen(cmd, 
			shell=True, stdout=subprocess.PIPE,
			preexec_fn=os.setsid)
		workers.append(sp)
	return workers

def terminate_background_services(workers):
	print(colored('Waiting for background services...','green'))
	q = Queue(maxsize=1)

	# DEPRECATED:
	def __timeout(signum,frame):
		signal.alarm(0) # Cancel further timeout
		print(colored('Ending background services...','green'))
		for p in workers:
			subprocess.Popen('kill {0}'.format(p.pid), 
				shell=True, stdout=subprocess.PIPE)
		# All done, unlock the queue
		q.task_done()

	# Terminate the first subprocess (ruby server)
	subprocess.Popen('kill {0}'.format(workers[0].pid),
		shell=True, stdout=subprocess.PIPE)


	# Wait for the rest
	wait_list  = workers[1:]
	if len(wait_list)==0: return

	pids       = [str(p.pid) for p in wait_list]
	print('waiting for : {0}'.format(','.join(pids)))
	exit_codes = [subp.wait() for subp in wait_list]


	print(colored('All subprocesses finished! Bye','green'))

	# signal.signal(signal.SIGALRM,__timeout)
	# signal.alarm(10) # seconds
	# q.put('wait')
	# q.join() # Block until it timeouts
	# q.get()

def print_record(rec):
	print(rec['tags'])

# Couple the processing pipe with the input
def process_with(pipe):
	def f(input0):
		Pipe.operate(pipe,input0)
	return f
	

if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Prepare word bag
	bag = wordbag.new()

	# Execute list of required background services
	services = [
		'ruby {0}/core/tokenizer/tokenizer.rb'.format(REPO_DIR),
		##'python3 {0}/core/textprocess.py'.format(REPO_DIR)
		]
	workers  = execute_background_services(services)

	# Delayed start
	time.sleep(1)

	# Prepare MQs for training sources
	qs = ['pantip-x1','pantip-x2','pantip-x3']
	mqs = [rabbit.create('localhost',q) for q in qs]

	# Prepare the processing pipeline (order matters)
	pipe = Pipe.new('preprocess',[])
	Pipe.push(pipe,preprocess.take)
	Pipe.push(pipe,rabbit.feed(mqs))
	Pipe.push(pipe,wordbag.feed(bag))
	Pipe.then(pipe,lambda out: print(colored('[DONE!]','cyan')))

	# Iterate through each record and process
	couch.each_do(db,process_with(pipe),limit=2400)

	# Disconnect from the MQs
	[rabbit.end(mq) for mq in mqs]

	# Waiting for the background services
	# and kill `em
	terminate_background_services(workers)

	# Report the collected word bag
	print(colored('[Word bag]','green'))
	words = sorted(bag.items(),key=lambda b: -b[1])[:50]
	pprint(words)
	# Print most recurring words to file
	with open(WORD_BAG_DIR,'w+') as txt:
		txt.writelines([w[0] + "\n" for w in words])

