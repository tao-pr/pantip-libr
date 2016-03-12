"""
Data Processing Pipeline
@starcolon projects
"""

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

	feed = rabbit.feed(dests)

	# Feed the outcome to destination MQs
	try:
		# Check if @outcome is iterable?
		iter_outcome = iter(outcome)
	except TypeError:
		# @outcome is not iterable
		feed(outcome)
	else:
		# @outcome is iterable
		[feed(r) for r in iter_outcome]

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

	feed = rabbit.feed(dests)

	n = 0
	# Transform the input one-by-one
	for s in _src:
		outcome = transformer(s)
		# Feed the record
		feed(outcome)

	print(colored(title,'cyan'), colored(' [DONE]','green'))	

	
