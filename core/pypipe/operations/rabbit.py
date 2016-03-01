"""
RabbitMQ data relay
@starcolon projects
"""

from termcolor import colored
from queue import Queue
import time
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

# Message generator
def iter(feeder):

	for methodframe, prop, body in feeder.channel.consume(feeder.q):
		try:
			print(body.decode('utf-8'))
			# TAODEBUG:
			print(methodframe)
			print('=================================')
			yield body
		except StopIteration:
			raise
		except Exception as e:
			print(colored('ERROR : {0}'.format(str(e)),'red'))

def end(feeder):
	conn,channel,q = feeder.components()
	conn.close()


