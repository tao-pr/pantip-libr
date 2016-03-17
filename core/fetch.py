"""
Fetch Pantip topics in the specified range
Extract key information for data mining
and push them into CouchDB

@starcolon projects
"""

from pypantip import scraper
from pydb import couch
from pprint import pprint
from termcolor import colored
import json

def scrape_and_store(topic_id):
	thread = scraper.scrape(_id)
	if thread is None: return False # Skip if thread scraping failed

	print(thread)

	# Save the scraped document
	print(colored('Saving ...','yellow'))
	couch.push(db,thread)

	return True

if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Fetch the threads in the specified range
	num = 0
	for _id in range(34803501,34806500):
		if scrape_and_store(_id): num += 1

	print(colored('=============================','cyan'))
	print(colored('  {0} documents processed'.format(num),'cyan'))
	print(colored('=============================','cyan'))
