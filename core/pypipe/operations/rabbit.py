"""
RabbitMQ data relay
@starcolon projects
"""

from termcolor import colored
from queue import Queue
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

# @param {list} of feeders
# @return {Record} it remains unchanged 
def feed(feeders):
	def feed_message(record):
		for feeder in feeders:
			conn,channel,q = feeder.components()
			topic_id  = record['topic_id']
			data = json.dumps(record,ensure_ascii=False)
			channel.basic_publish(
				exchange='',
				routing_key=q,
				body=data)
			print(colored('record #{0} fed to MQ '.format(topic_id),'cyan'),
				colored('#'+feeder.q,'white'))	
		return record
	return feed_message

# Another version of @feed, but this feeds a vector (list) instead 
def feed_str(feeders):
	def feed_v(vector):
		for feeder in feeders:
			conn,channel,q = feeder.components()
			channel.basic_publish(
				exchange='',
				routing_key=q,
				body=vector

		return vector
	return feed_v

# Message generator
def iter(feeder,transformation=lambda x:x):
	TIMEOUT = 3 # seconds
	# Start the awaiting signal
	try:
		def __timeout(signum,frame):
			raise StopIteration

		signal.signal(signal.SIGALRM,__timeout)
		signal.alarm(TIMEOUT) #TAOTODO: Place a timer here will break :(
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

def end(feeder):
	conn,channel,q = feeder.components()
	conn.close()


