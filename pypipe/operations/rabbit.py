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
	return (conn,channel)

def feed(feeder):
	def feed_message(record):
		conn,channel = feeder
		key  = record['topic_id']
		data = json.dumps(record,ensure_ascii=False)
		channel.basic_publish(
			exchange='',
			routing_key=str(key),
			body=data)
		print(colored('record #{0} fed to rabbit'.format(key),'blue'))

	return feed_message

def end(feeder):
	conn,channel = feeder
	conn.close()