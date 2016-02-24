"""
Librarian job
@starcolon projects
"""

from pypantip import scraper
from pydb import couch
from pprint import pprint
from termcolor import colored

if __name__ == '__main__':
	# Prepare the database server connection
	db = couch.connector('pantip')

	# Fetch the threads in the specified range
	for _id in range(34800000,34800100);
		thread = scraper.scrape(_id)

		# Save the scraped document
		print(colored('Saving ...','yellow'))
		couch.push(thread)


