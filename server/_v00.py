"""
Service provider v00

@starcolon projects
"""

import os
import json
from importlib.machinery import SourceFileLoader

REPO_DIR  = os.getenv('PANTIPLIBR','..')
MQ_INPUT  = 'feed-in'
MQ_OUTPUT = 'feed-out'


rabbit   = SourceFileLoader(
	'pypipe.operations.rabbit',
	REPO_DIR + 'core/pypipe/operations/rabbit.py'
).load_module()


def process(topic):
	# Push topic to the input MQ
	if not __is_valid(topic):
		return '{"error":true,"reason":"Invalid request structure"}'
	mqinput = rabbit.create('localhost',MQ_INPUT)
	rabbit.feed([mqinput])(topic)
	print('Message fed to input MQ')

	return json.dumps({
		"error": False,
		"result": None
	})

def __is_valid(topic):
	if topic is None:
		return False
	if len(topic)<2:
		return False
	if not ('title' in topic or 'topic' in topic):
		return False
	return True