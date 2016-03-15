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
VECT_COMPRESSOR_PATH  = '{0}/data/hasher/22'.format(REPO_DIR)
TAG_HASHER_PATH       = '{0}/data/hasher/33'.format(REPO_DIR)
TEXT_CLUSTER_PATH     = '{0}/data/cluster/00'.format(REPO_DIR)
CONTENT_CLUSTER_PATH  = '{0}/data/cluster/22'.format(REPO_DIR)
CLF_PATH              = '{0}/data/cluster/ff'.format(REPO_DIR)
STOPWORDS_PATH        = '{0}/data/words/stopwords.txt'.format(REPO_DIR)
CSV_REPORT_PATH       = '{0}/data/report.csv'.format(REPO_DIR)

# Prepare training arguments
arguments = argparse.ArgumentParser()
arguments.add_argument('--predim', type=int, default=800) # Dimension of preprocess text hasher
arguments.add_argument('--kcluster', type=int, default=4) # Number of text cluster
arguments.add_argument('--postdim', type=int, default=625) # Dimension of postprocess text hasher
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

		X2 <--  [tags, y1, SVD(X1)]
		Y2 <--  Sentiment score

	STEP#3 :: Train the classification

		(Y2,X2) -----> [@classification] ----> @model

	"""

	print(colored('==============================','cyan'))
	print(colored('  SENTIMENT TRAINING','cyan'))
	print()
	print(colored('  predim   : {0}'.format(args['predim']),'cyan'))
	print(colored('  postdim  : {0}'.format(args['postdim']),'cyan'))
	print(colored('  kcluster : {0}'.format(args['kcluster']),'cyan'))
	print(colored('  tagdim   : {0}'.format(args['tagdim']),'cyan'))
	print(colored('==============================','cyan'))

	# STEP#1
	#------------------------------------
	# Vectorise the input topic (text only) 
	mqx1     = rabbit.create('localhost','pantip-x1')
	mqvec12  = [
		rabbit.create('localhost','pantip-vector1'),
		rabbit.create('localhost','pantip-vector2')
	]
	topicHasher = texthasher.safe_load(
		TEXT_VECTORIZER_PATH,
		n_components=args['predim'],
		stop_words=stopwords
	)
	hashMe      = texthasher.hash(topicHasher,learn=True)

	print(colored('#STEP-1 started ...','cyan'))
	print('hasher : {0}'.format(topicHasher))
	DP.pipe(
		rabbit.iter(mqx1,take_x1),
		mqvec12,
		hashMe,
		title='Vectorisation'
	)

	rabbit.end(mqx1)
	rabbit.end_multiple(mqvec12)

	# Cluster the vectorised records with unsupervised clf
	mqvec1 = rabbit.create('localhost','pantip-vector1')
	mqcluster = [rabbit.create('localhost','pantip-cluster')]
	contentClf = textcluster.safe_load(
		CONTENT_CLUSTER_PATH,
		n_labels=args['kcluster']
	)
	clusterMe  = textcluster.classify(contentClf,learn=True)

	# Classification doesn't accept a generator,
	# So we need to roll the matrix out of the MQ
	srcmatrix = [np.array(json.loads(x)) for x in rabbit.iter(mqvec1)]
	
	DP.pipe(
		srcmatrix,
		mqcluster,
		clusterMe,
		title='Clustering'
	)

	print(colored('#STEP-1 finished ...','cyan'))

	rabbit.end(mqvec1)
	rabbit.end_multiple(mqcluster)


	# STEP#2
	# ---------------------------------------------
	# Assembly training vector and sentiment labels
	mqtags    = rabbit.create('localhost','pantip-x2') # User tags
	mqcluster = rabbit.create('localhost','pantip-cluster') # Cluster results
	mqsrc     = rabbit.create('localhost','pantip-vector2') # Hash matrix

	tags     = rabbit.iter(mqtags,take_tags)
	clusters = rabbit.iter(mqcluster)
	matV     = np.array([json.loads(v) for v in rabbit.iter(mqsrc)])

	# Decompose @matV with SVD
	mqveccontent    = rabbit.create('localhost','pantip-veccontent')
	topicCompressor = compressor.safe_load(
		VECT_COMPRESSOR_PATH,
		n_components=args['postdim']
	)
	compressMe = compressor.compress(topicCompressor,learn=True)
	DP.pipe(
		matV,
		[mqveccontent],	
		compressMe,
		title='Compressing Text'
	)
	
	# Convert tags into a numeric vector
	mqvectag  = rabbit.create('localhost','pantip-vectag')
	tagHasher = taghasher.safe_load(
		TAG_HASHER_PATH,
		n_feature=args['tagdim']
	)
	hashtagMe = taghasher.hash(tagHasher,learn=True)
	DP.pipe(
		tags,
		[mqvectag],
		hashtagMe,
		title='Tag Vectorising'
	)

	rabbit.end_multiple([mqtags,mqcluster,mqsrc])
	rabbit.end_multiple([mqvectag,mqveccontent])

	# STEP#3
	#----------------------------------------

	# Join each of the component together
	# Assembly a training vector
	mqy = rabbit.create('localhost','pantip-x3')
	Y = [y for y in rabbit.iter(mqy,take_sentiment_score)]

	mqx_cluster = rabbit.create('localhost','pantip-cluster')
	mqx_vec     = rabbit.create('localhost','pantip-veccontent')
	mqx_tag     = rabbit.create('localhost','pantip-vectag')
	XS = zip(
		[x for x in rabbit.iter(mqx_tag)],
		[x for x in rabbit.iter(mqx_cluster)],
		[x for x in rabbit.iter(mqx_vec)]
	)
	X = [json.loads(a) + [int(b)] + json.loads(c)
			for a,b,c in XS] # Concatenate vectors

	print(colored('[X] ','yellow'),len(X),' samples')
	for x in X:
		print('x[{0}] : '.format(len(x)), x[:6], '...')

	# Train!
	print(colored('Training process started...','cyan'))


	clf     = cluster.safe_load(CLF_PATH)
	trainMe = cluster.analyze(clf,labels=Y)
	Y_      = trainMe(X)
	print(colored('[DONE]','yellow'))

	rabbit.end_multiple([mqy,mqx_cluster,mqx_vec,mqx_tag])

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
		lbl_predict_rate.append('{0:.2f}'.format(accuracy))
	
	
	# Record the training accuracy to the CSV
	with open(CSV_REPORT_PATH,'a') as csv:
		csv.write('{0},{1},{3},{4},{5:.2f},{6}\n'.format(
			args['predim'], #0
			args['postdim'], #2,
			args['kcluster'], #3,
			args['tagdim'], #4
			predict_rate, #5
			lbl_predict_rate.join(',') #6
		))
	

	#Save the trained models
	if save:
		print(colored('Saving models...','cyan'))
		hasher.save(topicHasher,TEXT_VECTORIZER_PATH)
		textcluster.save(contentClf,CONTENT_CLUSTER_PATH)
		compressor.save(topicCompressor,VECT_COMPRESSOR_PATH)
		taghasher.save(tagHasher,TAG_HASHER_PATH)
		cluster.save(clf,CLF_PATH)
		print(colored('[DONE]','green'))



if __name__ == '__main__':

	print(colored('[WORKER STARTED!]','cyan'))

	# Load stop words from text file
	stopwords = load_stopwords()

	# Start the training process
	print(colored('Training centroid model ...','cyan'))
	output = train_sentiment_capture(stopwords)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
