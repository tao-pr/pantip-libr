"""
Batch topic request fire

@starcolon projects

"""

import requests
import json
import os
from termcolor import colored
import ..core.textprocess

REPO_DIR  = os.getenv('PANTIPLIBR','.')
couch = SourceFileLoader(
	'couch',
	REPO_DIR + 'core/pydb/couch.py'
).load_module()

URL = "http://0.0.0.0:5858/topic/00/sentiment"

def fire_request(skip):
	n = 0
	def _fire(record):
		n += 1
		if n<skip: return 

		print(colored('Firing request...','cyan'))
		resp = requests.post(URL,json=json.dumps(record,ensure_ascii=False))

		print(" API response: [{0}]".format(resp.status_code))
		print(resp.text)

	return _fire

def fire_em_all(skip,limit):
	db = couch.connector('pantip')
	couch.each_do(db,fire_request(skip),limit+skip)


if __name__ == '__main__':
	# Fire batch requests
	fire_em_all(skip=3,limit=1)

