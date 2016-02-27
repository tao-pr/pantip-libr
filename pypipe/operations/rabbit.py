"""
RabbitMQ data relay
@starcolon projects
"""

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
		data = json.dumps(record,ensure_ascii=False)
		channel.basic_publish(
			exchange='',
			routing_key=str(record['topic_id']),
			body=data)

	return feed_message

def end(feeder):
	conn,channel = feeder
	conn.close()