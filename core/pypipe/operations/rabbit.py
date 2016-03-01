"""
RabbitMQ data relay
@starcolon projects
"""

from termcolor import colored
from queue import Queue
import pika
import json

# Iterable feeder
class Feeder(object):
	def __init__(self,conn,channel,q):
		self.conn    = conn
		self.channel = channel
		self.q       = q
		# Use process queue to force async sync
		self.qtask   = Queue(maxsize=1) 

	def components(self):
		return (self.conn,self.channel,self.q)

	def __iter__(self):
		#TAODEBUG:
		print(colored('iter()','green'))
		return self

	def __next__(self):
		def __callback(channel,method,property,body):
			#TAOTODO: Check for empty queue
			self.qtask.put(body)
			self.qtask.join() # Block until the previous item has been checked out 

		self.channel.basic_consume(__callback,queue=self.q)
		#TAOTODO: Start following loop in a background thread
		#self.channel_start_consuming()

		while True:
			#TAODEBUG:
			print('@Waiting for message')
			next_up = self.qtask.get(True)

			#TAODEBUG:
			print('@Iter retrieved: ',str(next_up))

			if next_up is None:
				raise StopIteration
			else:
				yield next_up
				self.qtask.task_done() # Done!, signal the unblocking

def create(server_addr,q):
	conn = pika.BlockingConnection(pika.ConnectionParameters(server_addr))
	channel = conn.channel()
	channel.queue_declare(queue=q)
	feeder = Feeder(conn,channel,q)
	return feeder

# @return {Record} it remains unchanged 
def feed(feeder):
	def feed_message(record):
		conn,channel,q = feeder.components()
		topic_id  = record['topic_id']
		data = json.dumps(record,ensure_ascii=False)
		channel.basic_publish(
			exchange='',
			routing_key=q,
			body=data)
		print(colored('record #{0} fed to rabbit'.format(topic_id),'cyan'))	
		return record
	return feed_message

def end(feeder):
	conn,channel,q = feeder.components()
	conn.close()


