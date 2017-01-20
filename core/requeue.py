"""
Source MQ requeue task
@starcolon projects
"""

from pypipe import pipe as Pipe
from pypipe.operations import rabbit
import json

if __name__ == '__main__':
  qsrc = rabbit.create('localhost','pantip-x0')
  qdst = [rabbit.create('localhost',q) for q in ['pantip-x1','pantip-x2','pantip-x3','pantip-x00']]

  # Requeue!
  print('Requeuing ...')
  for m in rabbit.iter(qsrc):
    rabbit.feed(qdst)(m)  
  
  # Bye all queues!
  rabbit.end_multiple(qdst)
  rabbit.end(qsrc)

  # Transfer from temp MQ#00 to MQ#0
  q00 = rabbit.create('localhost','pantip-x00')
  q0 = rabbit.create('localhost','pantip-x0')
  for m in rabbit.iter(q00):
    rabbit.feed([q0])(m)

  # Bye all queues!
  rabbit.end_multiple([q0,q00])

  print('[DONE] All input queues are recycled.')