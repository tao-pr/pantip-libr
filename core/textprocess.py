"""
Text processing worker
@starcolon projects
"""

import os
import json
from termcolor import colored
from pypipe import pipe as Pipe
from pypipe.operations import rabbit
from pypipe.operations import tapper as T
from pypipe.operations import hasher
from pypipe.operations import cluster
from pypipe.operations import texthasher

REPO_DIR = os.getenv('PANTIPLIBR','../..')
TEXT_TRANSFORMER_PATH	= '{0}/data/hasher/00'.format(REPO_DIR)
CONTENT_CLUSTER_PATH = '{0}/data/cluster/00'.format(REPO_DIR)

def init_mqs():
	# Initialise rabbit MQ connectors
	mqsrcx = rabbit.create('localhost','pantip-centroidx')
	mqsrcy = rabbit.create('localhost','pantip-centroidy')
	return (mqsrcx,mqsrcy)

def end_mqs(mqs):
	mqsrc, mqdst = mqs
	rabbit.end(mqsrc)
	rabbit.end(mqdst)

# Convert the MQ record to an X vector (text only for hashing)
def take_x(record):
	data = json.loads(record)
	x = str(data['title'] + data['topic']) #TAOTOREVIEW: Any better compositon?
	return x

def take_y(record):
	data = json.loads(record)
	y = data['vote']
	return y


# Train the centroid clustering
def train_centroid(mqx,mqy,text_operations,clf):
	# Vectorise the input text X
	source = rabbit.iter(mqx,take_x)
	pipe = Pipe.new('centroid',[])

	# Vectorisation of X
	Pipe.push(pipe,texthasher.hash(text_operations,learn=True))
	Pipe.push(pipe,T.printtext(colored('[Output matrix X]','yellow')))
	Pipe.push(pipe,T.printdata)

	# Clustering
	labels = [y for y in rabbit.iter(mqy,take_y)]

	train_cluster = cluster.analyze(clf,labels)
	Pipe.push(pipe,T.printtext(colored('Clustering...','green')))
	Pipe.push(pipe,T.printtext('labels : {0}'.format(str(labels))))
	Pipe.push(pipe,train_cluster)
	Pipe.push(pipe,T.printtext(colored('[Output clusters]','yellow')))
	Pipe.push(pipe,T.printdata) #TAOTODO: Should visualise the plane

	# Self validation
	predict = cluster.analyze(clf)
	Pipe.push(pipe,T.printtext(colored('Validating...','green')))
	Pipe.push(pipe,predict)
	Pipe.push(pipe,T.printtext(colored('[Output clusters]','yellow')))
	Pipe.push(pipe,T.printdata)

	# Execute the training
	Pipe.operate(pipe,source)


if __name__ == '__main__':
	print(colored('[WORKER STARTED!]','cyan'))

	# Initialise working MQs
	mqsrcx, mqsrcy = init_mqs()

	# Initialise all text and feature hasher models
	print(colored('Initialising text hasher...','cyan'))
	text_operations = texthasher.new()

	print(colored('Initialising cluster operations...','cyan'))
	clf = cluster.new()

	# Start the training process
	print(colored('Training centroid model ...','cyan'))
	output = train_centroid(
		mqsrcx,
		mqsrcy,
		text_operations,
		clf
		)

	# End all working MQs
	print(colored('Ending MQs','cyan'))
	end_mqs((mqsrcx, mqsrcy))

	# Save the trained text transformer 
	print(colored('Saving text hasher','cyan'))
	texthasher.save(text_operations,TEXT_TRANSFORMER_PATH)

	# Save the trained classifier
	print(colored('Saving classifier','cyan'))
	cluster.save(clf,CONTENT_CLUSTER_PATH)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
