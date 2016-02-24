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

if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Fetch the threads in the specified range
	num = 0
	for _id in range(34800000,34800350):
		thread = scraper.scrape(_id)

		if thread is None: continue

		num = num + 1
		print(thread)

		# Save the scraped document
		print(colored('Saving ...','yellow'))
		couch.push(db,thread)

	print(colored('=============================',cyan))
	print(colored('  {0} documents processed'.format(num),'cyan'))
	print(colored('=============================',cyan))
