"""
Text processing worker
@starcolon projects
"""

import os
import json
from termcolor import colored
from pypipe.operations import rabbit
from pypipe.operations import texthasher

REPO_DIR = os.getenv('PANTIPLIBR','../..')
TEXT_TRANSFORMER_PATH	= '{0}/data/hasher/00'.format(REPO_DIR)

def init_mqs():
	# Initialise rabbit MQ connectors
	mqsrc = rabbit.create('localhost','pantip-centroid')
	mqdst = rabbit.create('localhost','pantipvec')
	return (mqsrc,mqdst)

def end_mqs(mqs):
	mqsrc, mqdst = mqs
	rabbit.end(mqsrc)
	rabbit.end(mqdst)

# Convert the MQ record to an X vector (text only for hashing)
def take_x(record):
	data = json.loads(record)
	x = str(data['title'] + data['topic']) #TAOTOREVIEW: Any better compositon?
	print(x) #TAODEBUG:
	return x

# Train the centroid clustering
def train_centroid(mq,text_operations):
	# Vectorise the input text
	source = rabbit.iter(mq,take_x)
	matrix = texthasher.hash(text_operations,learn=True)(source)

	#TAODEBUG:
	print(colored('[Output matrix]','yellow'))
	print(matrix)

	pass #TAOTODO:

if __name__ == '__main__':
	print(colored('[WORKER STARTED!]','cyan'))

	# Initialise working MQs
	mqsrc, mqdst = init_mqs()

	# Initialise all text and feature hasher models
	print(colored('Initialising text hasher...','cyan'))
	###TAOTODO:text_operations = texthasher.safe_load(TEXT_TRANSFORMER_PATH)
	text_operations = texthasher.new()

	# Start the training process
	print(colored('Training centroid model ...','cyan'))
	train_centroid(mqsrc,text_operations)

	# End all working MQs
	print(colored('Ending MQs','cyan'))
	end_mqs((mqsrc, mqdst))

	# Save the trained text transformer 
	print(colored('Saving text hasher','cyan'))
	texthasher.save(text_operations,TEXT_TRANSFORMER_PATH)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
