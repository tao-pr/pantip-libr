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
	p = Pool(processes=2)
	[title,topic] = p.map(tokenizer.tokenise,[title,topic])

	record['title'] = title
	record['topic'] = topic

	return record