"""
Source MQ requeue task
@starcolon projects
"""

from pypipe import pipe as Pipe
from pypipe.operations import rabbit
import json

if __name__ == '__main__':
	qsrc = rabbit.create('localhost','pantip-x0')
	qdst = [rabbit.create('localhost',q) for q in ['pantip-x1','pantip-x2','pantip-x3']]

	# Requeue!
	print('Requeuing ...')
	for m in rabbit.iter(qsrc):
		rabbit.feed(qdst)(m)
	
	# Bye all queues!
	rabbit.end_multiple(qdst)
	print('[DONE] All input queues are recycled.')