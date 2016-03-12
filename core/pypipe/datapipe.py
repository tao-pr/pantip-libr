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
# @param {Iterable} input MQ or any iterable
# @param {list} destination mq(s) to feed
# @param {Function} trasnformer function
# @param {String} title of this pipe (optional)
def pipe(src,dests,transformer=lambda d:d,title=''):
	feed = rabbit.feed(dests)

	# If @source is a rabbit feeder,
	# iter over it,
	# otherwise, treat it as is
	_src = rabbit.iter(src) if isinstance(src,rabbit.Feeder) else src

	n = 0
	for v in _src:
		feed(transformer(v))
		n += 1
	print(colored(title,'cyan'), colored(' [DONE]','green'))
	return n

# Zip two inputs together, transform with a 
# particular transformation and pump them
# into MQs
# @param {Iterable} input iterable #1
# @param {Iterable} input iterable #2
# @param {list} of destination MQs
# @param {String} title of this pipe (optional)
def pipezip(src1,src2,dests,transformer=lambda a,b:(a,b),title=''):
	def transform(tup):
		a,b = tup
		return transformer(a,b)
	return pipe(zip(src1,scr2),dests,transform,title)