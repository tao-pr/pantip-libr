"""
Tapper module for pipeline
@starcolon projects
"""

def printtext(str):
	def bypass(data):
		print(str)
		return data
	return bypass

def printdata(data):
	print(data)
	return data