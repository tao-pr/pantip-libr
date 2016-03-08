"""
Word bag for sentiment analysis
@starcolon projects
"""

def new():
	return {}

def feed(bag):
	def _feed(tokenised_rec):
		title = tokenised_rec['title']
		topic = tokenised_rec['topic']
		
		# Collect words
		for w in (title + topic).split():
			if len(w)>0:
				if w in bag: bag[w] += 1
				else: bag[w] = 1
	return _feed