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
STOPWORDS_PATH = '{0}/data/words/stopwords.txt'.format(REPO_DIR)

def init_mqs():
	# Initialise rabbit MQ connectors
	mqsrcx = rabbit.create('localhost','pantip-centroidx')
	mqsrcy = rabbit.create('localhost','pantip-centroidy')
	return (mqsrcx,mqsrcy)

def end_mqs(mqs):
	mqsrc, mqdst = mqs
	rabbit.end(mqsrc)
	rabbit.end(mqdst)

def load_stopwords():
	if (os.path.isfile(STOPWORDS_PATH)):
		with open(STOPWORDS_PATH,'r') as txt:
			return [w for w in txt.readlines() if len(w) > 0]
	else:
		print(colored('No stopwords definition file','red'))
		return []

# Convert the MQ record to an X vector (text only for hashing)
def take_x(record):
	data = json.loads(record)
	x = str(data['title'] + data['topic']) #TAOTOREVIEW: Any better compositon?
	return x

def take_y(record):
	data = json.loads(record)
	vote = data['vote']
	#['ขำกลิ้ง','สยอง','ถูกใจ','ทึ่ง','หลงรัก']
	positives = sum([v[1] for v in data['emoti'] if v[0] not in ['สยอง']])
	negatives = sum([v[1] for v in data['emoti'] if v[0] in ['สยอง']])

	# Classify by degree of attention & sentiments
	if vote + positives + negatives == 0:
		return 0 # Nobody cares
	if negatives > positives*0.67: # Negative
		return -1 # People dislike this
	if vote < 20: # Some people like it
		return 1
	if vote < 100: # may people love it
		return 5
	else:
		return 10 # Awesome post

	
def validate(predicted,truth):
	is_correct = predicted == truth
	if is_correct:
		print(colored('✔ {0}'.format(truth),'green'))
	else:
		print(colored('❌ {0} -- should be {1}'.format(predicted,truth),'red'))

	return is_correct

# @param {list} of boolean
def conclude_validation(results):
	num = len(results)
	pos = len([i for i in results if i])
	print(colored('=================','cyan'))
	print(colored('   ✱ {0} records'.format(num),'cyan'))
	print(colored('   ✱ {0}% correct'.format(100*pos/num),'cyan'))
	print(colored('=================','cyan'))

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
	Pipe.push(pipe,T.zip_with(validate,labels,lazy=False))
	Pipe.push(pipe,conclude_validation)

	# Execute the training
	Pipe.operate(pipe,source)


if __name__ == '__main__':
	print(colored('[WORKER STARTED!]','cyan'))

	# Initialise working MQs
	mqsrcx, mqsrcy = init_mqs()

	# Load stop words from text file
	stopwords = load_stopwords()

	# Initialise all text and feature hasher models
	print(colored('Initialising text hasher...','cyan'))
	text_operations = texthasher.new(stopwords)

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
