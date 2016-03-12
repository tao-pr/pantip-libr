"""
Data Processing Pipeline
@starcolon projects
"""

import json
import numpy as np
from .pipe import Pipe
from termcolor import colored
from .operations import rabbit
from .operations import tapper

# Pipe input to the destination MQ with
# particular transformation
# @param {Any} input
# @param {list} destination mq(s) to feed
# @param {Function} trasnformer function
# @param {String} title of this pipe (optional)
def pipe(src,dests,transform=lambda d:d,title=''):
	print(colored('  pipe @{0} started'.format(title),'yellow'))

	if isinstance(src,rabbit.Feeder):
		_src = rabbit.iter(src)
	else:
		_src = src
	
	# Transform the input at once
	outcome = transform(_src)
	safe_feed(dests,outcome)

	print(colored(title,'cyan'), colored(' [DONE]','green'))

# Pipe the list of input, one-by-one to the processing
# @param {Iterable} src
# @param {list} destination mq(s) to feed
# @param {Function} transformer function
# @param {String} title of this pipe (optional)
def pipe_each(src,dests,transform=lambda d:d,title=''):
	print(colored('  pipe @{0} started'.format(title),'yellow'))

	if isinstance(src,rabbit.Feeder):
		_src = rabbit.iter(src)
	else:
		_src = src

	n = 0
	# Transform the input one-by-one
	for s in _src:
		outcome = transformer(s)
		# Feed the record
		safe_feed(dests,outcome)

	print(colored(title,'cyan'), colored(' [DONE]','green'))	

	
# Safely dump a data to the destination MQs
# @param {list} of rabbit.Feeder
# @param {Any} list, iterable, numpy.array, object, etc.
#
# if @data is `iterable` ---> Feed each record per transaction
# otherwise, feed the bulk data once as a single transaction.
#
def safe_feed(mqs,data):
	feed = rabbit.feed(mqs)

	def to_str(el):
		if isinstance(el,np.ndarray):
			# Numpy array
			return json.dumps(list(el))
		elif type(data).__module__ == 'numpy':
			# Any numeric numpy types
			return str(el)
		elif isinstance(data,float) or isinstance(data,int):
			return str(el)
		else:
			try:
				return json.dumps(el)
			except TypeError:
				return str(el)
			else:
				return str(el)

	try:
		iterdata = iter(data)
	except TypeError:
		# @data is not iterable
		if type(data).__module__ == 'numpy':
			# It could be any numeric numpy types
			feed(str(data))
		elif isinstance(data,float) or isinstance(data,int):
			feed(str(data))
		else:
			# It could be any primitive / instance of any class
			feed(json.dumps(data))
	else:
		# @data is iterable
		if isinstance(data,str):
			# String does not need any conversion
			feed(data)
		else:
			# Elements of iterable type
			# will be fed individually
			[feed(to_str(r)) for r in iterdata]

