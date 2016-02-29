"""
Text processing worker
@starcolon projects
"""
from termcolor import colored
from ..pypipe.operations import rabbit
from ..pypipe.operations import hasher

def init_mqs():
	# Initialise rabbit MQ connectors
	mqsrc = rabbit.create('localhost','pantipsrc')
	mqdst = rabbit.create('localhost','pantipvec')
	return (mqsrc,mqdst)

def end_mqs(mqs):
	mqsrc, mqdst = mqs
	rabbit.end(mqsrc)
	rabbit.end(mqdst)

if __name__ == '__main__':
	#TAOTODO: Implement the worker
	print(colored('[WORKER STARTED!]','cyan'))

	# Initialise working MQs
	mqsrc, mqdst = init_mqs()
	

	# End all working MQs
	end_mqs(mqsrc, mqdst)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
