"""
Pantip thread record pre-processing pipe
@starcolon projects
"""

from multiprocessing import Pool
from . import tokenizer

def take(record):
	title = record['title']
	topic = record['topic']

	# Tokenise title & topic of the record
	pool = Pool(processes=2)
	[title,topic] = pool.map(tokenizer.tokenize,[title,topic])

	record['title'] = title
	record['topic'] = topic

	return record