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
		self.callback = lambda whatever: 
			print('{0} finished processing.'.format(title))


# Create a task pipeline
def make(title,tasks):
	return Pipe(title,tasks)

def set_callback(pipe,callback):
	pipe.callback = callback
	return pipe

# Append a new task into the existing pipe
def push(pipe,task):
	pipe.tasks.append(task)
	return pipe

def chain(pipe,nextpipe):
	pipe.callback = lambda final_out: operate(nextpipe, final_out)
	return pipe

# Execute the pipeline and take
# TAOTODO: This should be taken async
def operate(pipe,input0):
	print(colored('⏳ Executing {0}...'.format(pipe.title),'green'))
	if pipe is None:
		raise 'Pipe is not available'
	# NOTE: null is allowed as input

	# Sequential task runner
	def take(a,task):
		return task(a)

	out = reduce(take,pipe.tasks,input0)

	# Call the callback function
	pipe.callback(out) if pipe.callback is not None


