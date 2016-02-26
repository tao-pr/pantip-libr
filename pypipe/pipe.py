"""
Generic record processing pipeline.

@starcolon projects
"""

import pyspark
from functools import reduce

class Pipe:
	def __init__(self,title,tasks):
		self.title = title
		self.tasks = tasks[:]


# Create a task pipeline
def make(title,tasks):
	return Pipe(title,tasks)

# Execute the pipeline and take
def operate(pipe,input0,callback):
	print(colored('⏳ Executing {0}...'.format(pipe.title),'green'))
	if pipe is None:
		raise 'Pipe is not available'
	# NOTE: null is allowed as input

	# Sequential task runner
	def take(a,task):
		return task(a)

	out = reduce(take,pipe.tasks,input0)

	# Call the callback function
	callback(out) if callback is not None


