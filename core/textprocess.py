"""
Text processing worker
@starcolon projects
"""

import os
import json
from termcolor import colored
from pypipe import pipe as Pipe
from pypipe import datapipe as DP
from pypipe.operations import rabbit
from pypipe.operations import tapper as T
from pypipe.operations import cluster
from pypipe.operations import textcluster
from pypipe.operations import texthasher

REPO_DIR = os.getenv('PANTIPLIBR','../..')
TEXT_TRANSFORMER_PATH	= '{0}/data/hasher/00'.format(REPO_DIR)
TEXT_CLUSTER_PATH = '{0}/data/cluster/00'.format(REPO_DIR)
CONTENT_CLUSTER_PATH = '{0}/data/cluster/22'.format(REPO_DIR)
STOPWORDS_PATH = '{0}/data/words/stopwords.txt'.format(REPO_DIR)

def load_stopwords():
	if (os.path.isfile(STOPWORDS_PATH)):
		with open(STOPWORDS_PATH,'r') as txt:
			return [w for w in txt.readlines() if len(w) > 0]
	else:
		print(colored('No stopwords definition file','red'))
		return []

# Convert the MQ record to an X vector (text only for hashing)
def take_x1(record):
	data = json.loads(record)
	x = str(data['title'] + data['topic']) #TAOTOREVIEW: Any better compositon?
	return x

def take_sentiment_score(record):
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
	if vote < 100: # Many people love it
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
def train_centroid(stopwords):

	"""
	STEP#1 :: Cluster topic with unsupervised classification

		X1 text ---> [@cluster] ----> (y1 group, X1 text)

	STEP#2 :: Combine topic, tags, and group to make feature vector

		X2 <--  [tags, y1, SVD(X1)]
		Y2 <--  Sentiment score

	STEP#3 :: Train the classification

		(Y2,X2) -----> [@classification] ----> @model

	"""

	# STEP#1
	#------------------------------------
	# Vectorise the input topic (text only) 
	mqsrc  = rabbit.create('localhost','pantip-x1')
	mqdst  = rabbit.create('localhost','pantip-x2')
	hasher = texthasher.safe_load(TEXT_TRANSFORMER_PATH)
	hashMe = texthasher.hash(hasher,learn=True)

	print(colored('#STEP-1 started ...','cyan'))
	print('hasher : {0}'.format(hasher))
	DP.pipe(
		rabbit.iter(mqsrc,take_x1),
		[mqdst],
		hashMe,
		title='Vectorisation'
	)

	rabbit.end(mqsrc)
	rabbit.end(mqdst)

	# Cluster the vectorised records with unsupervised clf
	mqsrc = rabbit.create('localhost','pantip-x2')
	mqdst = [
		rabbit.create('localhost','pantip-x3'),
		rabbit.create('localhost','pantip-y1')
	]
	tc = textcluster.safe_load(CONTENT_CLUSTER_PATH)
	clusterMe = textcluster.classify(tc,learn=True)
	DP.pipe(mqsrc,mqdst,clusterMe,title='Clustering')

	rabbit.end(mqsrc)
	rabbit.end_multiple(mqdst)

	print(colored('#STEP-1 finished ...','cyan'))

	# TAOTODO:
	# STEP#2
	# ---------------------------------------------
	# Assembly traning vector and sentiment labels


	pass



if __name__ == '__main__':
	print(colored('[WORKER STARTED!]','cyan'))

	# Load stop words from text file
	stopwords = load_stopwords()

	# Start the training process
	print(colored('Training centroid model ...','cyan'))
	output = train_centroid(stopwords)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
