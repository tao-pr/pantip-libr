"""
Text processing worker
@starcolon projects
"""
from termcolor import colored
from pypipe.operations import rabbit
from pypipe.operations import hasher

TEXT_VECTORIZER_PATH	= 'data/transformer/00'

def init_mqs():
	# Initialise rabbit MQ connectors
	mqsrc = rabbit.create('localhost','pantipsrc')
	mqdst = rabbit.create('localhost','pantipvec')
	return (mqsrc,mqdst)

def end_mqs(mqs):
	mqsrc, mqdst = mqs
	rabbit.end(mqsrc)
	rabbit.end(mqdst)

def init_vectorizer():
	print(colored('Loading text vectoriser...','green'))
	return hasher.safe_load(TEXT_VECTORIZER_PATH)

def save_vectorizer(vectorizer):
	print(colored('Saving text vectoriser...','green'))
	hasher.save(vectorizer,TEXT_VECTORIZER_PATH)

if __name__ == '__main__':
	print(colored('[WORKER STARTED!]','cyan'))

	# Initialise working MQs
	mqsrc, mqdst = init_mqs()

	# Initialise the vectoriser objects
	vectorizer = init_vectorizer()

	# TAOTODO: Process the workers	

	# End all working MQs
	end_mqs((mqsrc, mqdst))

	# Save the vectoriser
	save_vectorizer(vectorizer)

	# Bye
	print(colored('[WORKER FINISHED!]','cyan'))
