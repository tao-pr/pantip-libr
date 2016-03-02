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
	TIMEOUT = 3 # seconds
	# Start the awaiting signal
	try:
		def __timeout(signum,frame):
			raise StopIteration

		signal.signal(signal.SIGALRM,__timeout)
		signal.alarm(TIMEOUT)
		for methodframe, prop, body in feeder.channel.consume(feeder.q):
			signal.alarm(0)
			print(body.decode('utf-8')[:10])

			msg = body.decode('utf-8')
			yield msg
			feeder.channel.basic_ack(methodframe.delivery_tag)
			
			# Startover a new timer
			signal.alarm(TIMEOUT)
	
	except StopIteration as e:
		signal.alarm(0) # Cancel the timer
		print('--end of queue--')
		raise
	except Exception as e:
		signal.alarm(0) 
		raise

def end(feeder):
	conn,channel,q = feeder.components()
	conn.close()


