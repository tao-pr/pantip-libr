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
from collections import dequeue
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

	# Wait for child processes (apart from the ruby server)
	# to finish
	wait_list = workers[1:] # The 1st is server, skip it

	while len(wait_list)>0:
		p = wait_list.pop()
		try:
			os.kill(p.pid,0) #This won't force termination if still running
		except OSError:
			# @p has already finished and died
			pass
		else:
			# @p is still running
			wait_list.appendleft(p)


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
		'python3 {0}/core/textprocess.py > textprocess.log'.format(REPO_DIR)
		]
	workers  = execute_background_services(services)

	# Delayed start
	time.sleep(1)

	# Prepare MQs for training sources
	qs = ['pantip-x1','pantip-x2']
	mqs = [rabbit.create('localhost',q) for q in qs]

	#TAOTODO: Empty the MQs before starting

	# Prepare the processing pipeline (order matters)
	pipe = Pipe.new('preprocess',[])
	Pipe.push(pipe,preprocess.take)
	Pipe.push(pipe,rabbit.feed(mqs))
	Pipe.push(pipe,wordbag.feed(bag))
	Pipe.then(pipe,lambda out: print(colored('[DONE!]','cyan')))

	# Iterate through each record and process
	couch.each_do(db,process_with(pipe),limit=20)

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

