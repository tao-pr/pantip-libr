"""
RabbitMQ data relay
@starcolon projects
"""

import pika
import json

# Feed the record to the specified RabbitMQ channel
def feed(server_addr,q):
	feeder = __make_rabbit_feeder(server_addr,q)
	def feed_message(record):
		conn,channel = feeder
		data = json.dumps(record,ensure_ascii=False)
		channel.basic_publish(
			exchange='',
			routing_key=record['topic_id'],
			body=data)
		__end_feeder(feeder)

	return feed_message

def __make_rabbit_feeder(server_addr,q):
	conn = pika.BlockingConnection(pika.ConnectionParameters(server_addr))
	channel = conn.channel()
	channel.declare_queue(queue=q)
	return (conn,channel)

def __end_feeder(feeder):
	conn,channel = feeder
	conn.close()