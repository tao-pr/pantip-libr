"""
Pantip thread record pre-processing pipe
@starcolon projects
"""

from multiprocessing import Pool
from termcolor import colored
from . import tokenizer
import json

def take(record):
	package = {
		'data':[record['title'],record['topic']]
	}
	
	results = tokenizer.tokenize(json.dumps(package,ensure_ascii=False))
	record['title'] = ' '.join(results['data'][0])
	record['topic'] = ' '.join(results['data'][1])

	return record


