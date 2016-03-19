"""
Service provider v00

@starcolon projects
"""

def process(topic):
	# Push topic to the input MQ
	# TAOTODO:
	if not __is_valid(topic):
		return '{"error":true,"reason":"Invalid request structure"}'
	pass

def __is_valid(topic):
	if not ('title' in topic or 'topic' in topic):
		return False
	return True