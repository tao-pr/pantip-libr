"""
Text processing worker
@starcolon projects
"""

import json
from termcolor import colored
from pypipe.operations import rabbit
from pypipe.operations import hasher

TEXT_TRANSFORMER_PATH	= 'data/transformer/00'

def init_mqs():
	# Initialise rabbit MQ connectors
	mqsrc = rabbit.create('localhost','pantip-centroid')
	mqdst = rabbit.create('localhost','pantipvec')
	return (mqsrc,mqdst)

def end_mqs(mqs):
	mqsrc, mqdst = mqs
	rabbit.end(mqsrc)
	rabbit.end(mqdst)

def init_transformer():
	print(colored('Loading text transformer...','green'))
	return hasher.safe_load(TEXT_TRANSFORMER_PATH)

def save_transformer(vectorizer):
	print(colored('Saving text transformer...','green'))
	hasher.save(vectorizer,TEXT_TRANSFORMER_PATH)

# Train the centroid clustering
def train_centroid(mq):
	pass

if __name__ == '__main__':
	print(colored('[WORKER STARTED!]','cyan'))

	# Initialise working MQs
	mqsrc, mqdst = init_mqs()

	# Initialise the text transformer objects
	transformer = init_transformer()

	# Start the training process
	print(colored('Preparing lazy training set ...','cyan'))
	train_centroid(mqsrc)

	# End all working MQs
	print(colored('Ending MQs','cyan'))
	end_mqs((mqsrc, mqdst))

	# Save the trained text transformer 
	print(colored('Saving transfomer','cyan'))
	save_transformer(transformer)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
