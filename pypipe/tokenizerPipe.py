"""
Word tokeniser pipe
@starcolon projects
"""

from . import pipe
from tornado import httpclient
from termcolor import colored

tokeniser_serv = 'http://localhost:9861/break/'

def new(title):
	def action(input0):
		output = tokenize(input0)
		# TAOTODO: It should pass output through the pipe.callback
		# How?? 
	return pipe.make(title,[action])

# @input: String
# @output: list of string
def tokenize(phrase):
	# Do not proceed with empty input
	if phrase is None: return []
	if len(phrase)==0: return []

	# Generate a tokenising request
	return __request(phrase)

# Make a request to the tokeniser service
def __request(input0):
	client = httpclient.HTTPClient()
	output = None
	try:
		print('tokenising.. '.yellow + input0)
		req    = httpclient.HTTPRequest(tokeniser_serv,method='POST')
		resp   = client.fetch(req)
		output = resp.body
	except httpclient.HTTPError as e:
		# HTTP error header
		print(colored('HTTP Error : ' + str(e),'red'))
	except e:
		# Some unhandled error
		print(colored('ERROR : ' + str(e), 'red'))

	client.close()

	# TAODEBUG:
	print(colored(output,'white'))

	return output
