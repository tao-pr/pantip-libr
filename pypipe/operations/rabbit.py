"""
RabbitMQ data relay
@starcolon projects
"""

from termcolor import colored
import pika
import json

def create(server_addr,q):
	conn = pika.BlockingConnection(pika.ConnectionParameters(server_addr))
	channel = conn.channel()
	channel.queue_declare(queue=q)
	return (conn,channel,q)

# @return {Record} it remains unchanged 
def feed(feeder):
	def feed_message(record):
		conn,channel,q = feeder
		topic_id  = record['topic_id']
		data = json.dumps(record,ensure_ascii=False)
		channel.basic_publish(
			exchange='',
			routing_key=q,
			body=data)
		print(colored('record #{0} fed to rabbit'.format(topic_id),'cyan'))	
		return record
	return feed_message

def pull(feeder):
	def __callback(ch, method, properties, body):
		pass #TAOTODO:
	conn,channel,q = feeder
	channel.basic_consume(__callback,q,no_ack=True)

def end(feeder):
	conn,channel,q = feeder
	conn.close()

# TAOTODO: Make an iterable over the MQ feeder
def make_iterable(feeder):
	pass