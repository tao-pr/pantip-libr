"""
Tapper utility for pipeline
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

# This only works if the data is a {list}
def zip_with(zipper):
	def zip_(data):
		return [zipper(a,b) for a in data]
	return zip_