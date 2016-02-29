"""
RabbitMQ data relay
@starcolon projects
"""

from termcolor import colored
import pika
import json

class Feeder(object):
	def __init__(self,conn,channel,q):
		self.conn    = conn
		self.channel = channel
		self.q       = q

	def get_params(self):
		return (self.conn,self.channel,self.q)

	def __iter__(self):
		#TAOTODO: Pull the next message out of the queue
		pass

def create(server_addr,q):
	conn = pika.BlockingConnection(pika.ConnectionParameters(server_addr))
	channel = conn.channel()
	channel.queue_declare(queue=q)
	feeder = Feeder(conn,channel,q)
	return feeder

# @return {Record} it remains unchanged 
def feed(feeder):
	def feed_message(record):
		conn,channel,q = feeder.get_params()
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
	conn,channel,q = feeder.get_params()
	conn.close()

