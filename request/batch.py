"""
Batch topic request fire

@starcolon projects

"""

import requests
import json
from termcolor import colored

URL = "http://0.0.0.0:5858/topic/00/sentiment"

def fire_request(title,topic):
	print(colored('Firing request...','cyan'))
	data = {"title": title, "topic": topic}
	resp = requests.post(URL,json=json.dumps(data,ensure_ascii=False))

	print(" API response: [{0}]".format(resp.status_code))
	print(resp.text)


if __name__ == '__main__':
	# Fire batch requests
	ammos = [
		["หัวข้อทดสอบ","รายละเอียดกระทู้ทดสอบ"]
	]

	for ammo in ammos:
		fire_request(ammo[0],ammo[1])

	pass 
