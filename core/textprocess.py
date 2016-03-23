"""
Text processing worker
@starcolon projects
"""

import os
import sys
import json
import argparse
import numpy as np
from termcolor import colored
from pypipe import pipe as Pipe
from pypipe import datapipe as DP
from pypipe.operations import rabbit
from pypipe.operations import tapper as T
from pypipe.operations import cluster
from pypipe.operations import taghasher
from pypipe.operations import texthasher
from pypipe.operations import compressor
from pypipe.operations import textcluster


REPO_DIR = os.getenv('PANTIPLIBR','../..')
TEXT_VECTORIZER_PATH	= '{0}/data/hasher/00'.format(REPO_DIR)
TAG_HASHER_PATH       = '{0}/data/hasher/33'.format(REPO_DIR)
TEXT_CLUSTER_PATH     = '{0}/data/cluster/00'.format(REPO_DIR)
CONTENT_CLUSTER_PATH  = '{0}/data/cluster/22'.format(REPO_DIR)
CLF_PATH              = '{0}/data/cluster/ff'.format(REPO_DIR)
STOPWORDS_PATH        = '{0}/data/words/stopwords.txt'.format(REPO_DIR)
CSV_REPORT_PATH       = '{0}/data/report.csv'.format(REPO_DIR)

# Prepare training arguments
arguments = argparse.ArgumentParser()
arguments.add_argument('--dim', type=int, default=800) # Dimension of preprocess text hasher
arguments.add_argument('--kcluster', type=int, default=4) # Number of text cluster
arguments.add_argument('--tagdim', type=int, default=16) # Dimension of tag after hash
args = vars(arguments.parse_args(sys.argv[1:]))

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

def take_tags(record):
	data = json.loads(record)
	x = ' '.join([tag for tag in data['tags'] if len(tag)>1])
	return x

def take_sentiment_score(record):
	data = json.loads(record)
	vote = data['vote']
	#['ขำกลิ้ง','สยอง','ถูกใจ','ทึ่ง','หลงรัก']
	positives = sum([v[1] for v in data['emoti'] if v[0] not in ['สยอง']])
	negatives = sum([v[1] for v in data['emoti'] if v[0] in ['สยอง']])

	# Classify by degree of attention & sentiments
	if negatives >= 3: # Negative
		return -1 # People dislike this
	if vote + positives + negatives == 0:
		return 0 # Nobody cares
	if vote < 12: # Some like it
		return 1
	else:
		return 10 # Popular post

	
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
def train_sentiment_capture(stopwords,save=False):

	"""
	STEP#1 :: Cluster topic with unsupervised classification

		X1 text ---> [@cluster] ----> (y1 group, X1 text)

	STEP#2 :: Combine topic, tags, and group to make feature vector

		X2 <--  [tags, y1, X1]
		Y2 <--  Sentiment score

	STEP#3 :: Train the classification

		(Y2,X2) -----> [@classification] ----> @model

	"""

	print(colored('==============================','cyan'))
	print(colored('  SENTIMENT TRAINING','cyan'))
	print()
	print(colored('  DIM   : {0}'.format(args['dim']),'cyan'))
	print(colored('  K     : {0}'.format(args['kcluster']),'cyan'))
	print(colored('  TAG   : {0}'.format(args['tagdim']),'cyan'))
	print(colored('==============================','cyan'))

	# STEP#1
	#------------------------------------
	# Vectorise the input topic (text only) 
	mqx1     = rabbit.create('localhost','pantip-x1')
	topicHasher = texthasher.safe_load(
		TEXT_VECTORIZER_PATH,
		n_components=args['dim'],
		stop_words=stopwords,
		decomposition='SVD'
	)
	hashMe = texthasher.hash(topicHasher,learn=True)

	print(colored('#STEP-1 started ...','cyan'))
	print('hasher : {0}'.format(topicHasher))
	iterX = DP.pipe(
		rabbit.iter(mqx1,take_x1),
		dests=None,
		transform=hashMe,
		title='Vectorisation'
	)

	rabbit.end(mqx1)

	vecX = [x for x in iterX]

	# Cluster the vectorised records with unsupervised clf
	contentClf = textcluster.safe_load(
		CONTENT_CLUSTER_PATH,
		n_labels=args['kcluster']
	)
	clusterMe  = textcluster.classify(contentClf,learn=True)

	# Classification doesn't accept a generator,
	# So we need to roll the matrix out of the MQ
	clusters = DP.pipe(
		[x for x in vecX],
		dests=None,
		transform=clusterMe,
		title='Clustering'
	)

	print(colored('#STEP-1 finished ...','cyan'))


	# STEP#2
	# ---------------------------------------------
	# Vectorise tags	
	
	# Convert tags into a numeric vector
	tagHasher = taghasher.safe_load(
		TAG_HASHER_PATH,
		n_feature=args['tagdim']
	)
	mqx2      = rabbit.create('localhost','pantip-x2')
	hashtagMe = taghasher.hash(tagHasher,learn=True)
	vectags   = DP.pipe(
		[tag for tag in rabbit.iter(mqx2,take_tags)],
		dests=None,
		transform=hashtagMe,
		title='Tag Vectorising'
	)

	rabbit.end(mqx2)	
	
	# STEP#3
	#----------------------------------------
	# Join each of the component together
	# Assembly a training vector
	mqy = rabbit.create('localhost','pantip-x3')
	Y = [y for y in rabbit.iter(mqy,take_sentiment_score)]

	XS = zip(
		list(vectags),
		[[i] for i in clusters], # Make scalar a single-element vector
		list(vecX)
	)

	X = [list(a) + list(b) + list(c) for a,b,c in XS]

	rabbit.end(mqy)

	# Train!
	print(colored('Training process started...','cyan'))


	clf     = cluster.safe_load(CLF_PATH)
	trainMe = cluster.analyze(clf,labels=Y)
	Y_      = trainMe(X)
	print(colored('[DONE]','yellow'))

	# Self-validation
	num_correct  = len([1 for y,y0 in zip(Y_,Y) if y==y0])
	predict_rate = 100*float(num_correct)/float(len(Y))
	print(colored('====== TRAINING LABELS =====','magenta'))
	print(Y)
	print(colored('========= PREDICTED ========','magenta'))
	print(list(Y_))
	print(colored('=========== RESULTS ========','magenta'))
	print('    overall accuracy:   {0:.2f} %'.format(predict_rate))

	# Report accuracy by each of the labels
	labels = list(set(Y_))
	lbl_predict_rate = []
	for lbl in labels:
		samples = [(y,y0) for y,y0 in zip(Y_,Y) if y0==lbl]
		num_correct = len([1 for y,y0 in samples if y==y0])
		num_all     = len(samples)
		accuracy    = 100*float(num_correct)/float(num_all)
		
		print('    accuracy class #{0} :    {1:.2f} % (out of {2} cases)'.format(lbl,accuracy,num_all))
		lbl_predict_rate.append('{0:.2f}'.format(accuracy).center(7))
	
	
	# Record the training accuracy to the CSV
	with open(CSV_REPORT_PATH,'a') as csv:
		csv.write('{0},{1},{2},{3},{4}\n'.format(
			str(args['dim']).center(4), #0
			str(args['kcluster']).center(3), #1,
			str(args['tagdim']).center(5), #2
			'{0:.2f}'.format(predict_rate).center(7), #3
			','.join(lbl_predict_rate) #4
		))
	

	#Save the trained models
	if save:
		print(colored('Saving models...','cyan'))
		hasher.save(topicHasher,TEXT_VECTORIZER_PATH)
		textcluster.save(contentClf,CONTENT_CLUSTER_PATH)
		taghasher.save(tagHasher,TAG_HASHER_PATH)
		cluster.save(clf,CLF_PATH)
		print(colored('[DONE]','green'))


def load_models():
	topicHasher = hasher.safe_load(TEXT_VECTORIZER_PATH)
	tagHasher   = tagHasher.safe_load(TAG_HASHER_PATH)
	contentClf  = textcluster.safe_load(CONTENT_CLUSTER_PATH)
	clf         = cluster.safe_load(CLF_PATH)
	return (topicHasher,taghasher,contentClf,clf)

# @param {iterable} topics
def classify_text(topicHasher,tagHasher,contentClf,clf):
	def _classify(textsrc):
		print(colored('[Classifying]...','green'))
		# Prepare operations
		hashMe     = texthasher.hash(topicHasher,learn=False)
		clusterMe  = textcluster.classify(contentClf,learn=False)
		hashtagMe  = taghasher.hash(tagHasher,learn=False)
		classifyMe = cluster.analyze(clf)
	
		iterX = DP.pipe(
			[take_x1(x) for x in textsrc],
			dests=None,
			transform=hashMe,
			title='Vectorisation'
		)

		vecX = [x for x in iterX]

		clusters = DP.pipe(
			[x for x in vecX],
			dests=None,
			transform=clusterMe,
			title='Clustering'
		)

		vectags   = DP.pipe(
			[take_tags(x) for x in textsrc],
			dests=None,
			transform=hashtagMe,
			title='Tag Vectorising'
		)

		XS = zip(
			list(vectags),
			[[i] for i in clusters], # Make scalar a single-element vector
			list(vecX)
		)
		X = [list(a) + list(b) + list(c) for a,b,c in XS]

		# Analyse 
		Y_ = classifyMe(X)

		# Returns the results as tuples
		return zip(Y_,X)
	return _classify


if __name__ == '__main__':

	print(colored('[WORKER STARTED!]','cyan'))

	# Load stop words from text file
	stopwords = load_stopwords()

	# Start the training process
	print(colored('Training centroid model ...','cyan'))
	output = train_sentiment_capture(stopwords)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
