"""
Batch topic request fire

@starcolon projects

"""

import requests
import json
import os
from couchdb.client import Server
from termcolor import colored

REPO_DIR  = os.getenv('PANTIPLIBR','.')
URL = "http://0.0.0.0:5858/topic/00/sentiment"

def fire_request(record):	
	print(colored('Firing request...','cyan'))
	resp = requests.post(URL,json=json.dumps(record,ensure_ascii=False))

	print(" API response: [{0}]".format(resp.status_code))
	print(resp.text)


def fire_em_all(skip,limit):
	collection = 'pantip'
	svr = Server()
	if collection not in svr:
		src = svr.create(collection)
	else:
		src = svr[collection]

	# Iterate through the collection and fire
	n = 0
	n_processed = 0
	for _id in src:
		n += 1
		rec = src.get(_id)
		if n<skip: continue

		if n_processed>limit:
			print(colored('Out of ammo!','red'))
			return 

		# Fire a single request
		print(colored('Firing #{0}'.format(_id)))
		fire_request(rec)
		n_processed += 1


if __name__ == '__main__':
	# Fire batch requests
	fire_em_all(skip=3,limit=1)

