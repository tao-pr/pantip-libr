"""
Generic record processing pipeline.

@starcolon projects
"""

import pyspark
from termcolor import colored
from functools import reduce


class Pipe:
	def __init__(self,title,tasks):
		self.title = title
		self.tasks = tasks[:]
		self.then = lambda whatever: print(
			'{0} finished processing.'.format(title))


# Create a task pipeline
def new(title,tasks):
	return Pipe(title,tasks)

def then(pipe,callback):
	pipe.then = callback
	return pipe

def join(pipe1,pipe2):
	pipe1.then = lambda output: operate(pipe2,output)
	return pipe1

# Append a new task into the existing pipe
def push(pipe,task):
	pipe.tasks.append(task)
	return pipe

# This will chain the next pipe via callback
def chain(pipe,nextpipe):
	pipe.then = lambda final_out: operate(nextpipe, final_out)
	return pipe

# Execute the pipeline and take
def operate(pipe,input0):
	print(colored('⏳ Executing {0}...'.format(pipe.title),'green'))
	if pipe is None:
		raise 'Pipe is not available'
	# NOTE: null is allowed as input

	# Sequential task runner
	def take(a,task):
		return task(a)

	out = reduce(take,pipe.tasks,input0)

	# Send the output via callback
	if pipe.then is not None: 
		pipe.then(out)
	else:
		print('[Then] is not supplied.') # TAODEBUG:


