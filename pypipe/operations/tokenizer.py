"""
String tokeniser operation
@starcolon projects
"""
from tornado import httpclient
from termcolor import colored

tokeniser_serv = 'http://localhost:9861/break/'

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
		print(colored('tokenising.. ','yellow') + input0)
		req    = httpclient.HTTPRequest(tokeniser_serv,method='POST',body=input0)
		resp   = client.fetch(req)
		output = resp.body
	except httpclient.HTTPError as e:
		# HTTP error header
		print(colored('HTTP Error : ' + str(e),'red'))
	except Exception as e:
		# Some unhandled error
		print(colored('ERROR : ' + str(e), 'red'))

	client.close()

	# TAODEBUG:
	print(colored('{Tokenizer received:}','white'))
	print(colored(output,'white'))

	return output
