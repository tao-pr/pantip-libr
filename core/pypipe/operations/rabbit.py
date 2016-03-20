"""
RabbitMQ data relay
@starcolon projects
"""


from termcolor import colored
from queue import Queue
import numpy as np
import signal
import time
import pika
import json

# Iterable feeder
class Feeder(object):
	def __init__(self,conn,channel,q):
		self.conn    = conn
		self.channel = channel
		self.q       = q
	def components(self):
		return (self.conn,self.channel,self.q)

		

def create(server_addr,q):
	conn = pika.BlockingConnection(pika.ConnectionParameters(server_addr))
	channel = conn.channel()
	channel.queue_declare(queue=q)
	feeder = Feeder(conn,channel,q)
	return feeder

def purge(feeder,qlist):
	conn,channel,q = feeder.components()
	for q in qlist:
		try:
			channel.queue_purge(q)
		except pika.exceptions.ChannelClosed:
			# Q is not up, but we ignore the unwanted error
			pass

# @param {list} of feeders
# @return {Record} it remains unchanged 
def feed(feeders):
	def feed_message(record,no_parse=False):
		for feeder in feeders:
			conn,channel,q = feeder.components()
			
			# Make sure the data type is compatible
			if isinstance(record,str) or no_parse:
				data = record
			else:
				data = json.dumps(record,ensure_ascii=False)

			try:
				channel.basic_publish(
					exchange='',
					routing_key=q,
					body=data)
			except Exception:
				print(colored('ERROR publishing to MQ #','red'),q)
				raise
		return record
	return feed_message


# Message generator
def iter(feeder,transformation=lambda x:x):
	TIMEOUT = 5 # seconds
	# Start the awaiting signal
	try:
		def __timeout(signum,frame):
			raise StopIteration

		signal.signal(signal.SIGALRM,__timeout)
		signal.alarm(TIMEOUT)
		for methodframe, prop, body in feeder.channel.consume(feeder.q):
			signal.alarm(0)
			msg = transformation(body.decode('utf-8'))
			
			yield msg
			feeder.channel.basic_ack(methodframe.delivery_tag)
			
			# Startover a new timer
			signal.alarm(TIMEOUT)
	
	except StopIteration as e:
		signal.alarm(0) # Cancel the timer
		print(colored('--Timeout, no further message--','magenta'))
		raise
	except Exception as e:
		signal.alarm(0) 
		print(colored('--Exception broke the iteration--','magenta'))
		raise

# Start a message listening loop (endless)
def listen(feeder,callback):
	def on_message(ch,method,prop,body):
		# Trigger the callback
		callback(body.decode('utf-8'))
		ch.basic_ack(method.delivery_tag)
	feeder.channel.basic_qos(prefetch_count=1)
	feeder.channel.basic_consume(on_message,queue=feeder.q)
	feeder.channel.start_consuming()


def end(feeder):
	print(colored('Ending MQ #','white'),feeder.q)
	try:
		conn,channel,q = feeder.components()
		conn.close()
	except pika.exceptions.ConnectionClosed:
		print(colored('MQ appeared offline','red'))
		

def end_multiple(feeders):
	[end(f) for f in feeders]


