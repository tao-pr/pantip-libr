"""
Pantip Scraper
@starcolon projects
"""

from htmldom import htmldom
from termcolor import colored

def scrape(topic_id):
	# Download the topic and create DOM over it
	url  = 'http://www.pantip.com/topic/{0}'.format(topic_id)
	print(colored('Fetching: ','green') + colored(url,'cyan'))
	page = htmldom.HtmlDom(url).createDom()

	# Deleted topic?
	if page.find('.callback-status') \
	and 'กระทู้นี้ถูกลบเนื่องจาก' in page.find('.callback-status').text():
		print(colored('DELETED TOPIC','red'))
		return None

	# Extract the content out of the page
	title = page.find('h2.display-post-title').text()
	topic = page.find('.display-post-story').text()
	tags  = parse_tags(page.find('.display-post-tag-wrapper')[:])
	svote = page.find('.like-score').text()
	vote  = int(svote) if svote else 0
	emoti = extract_emotions(page.find('.emotion-vote-user').text())

	# Formulate the scraped document
	scrape = {
		'topic_id': topic_id,
		'title': title,
		'topic': topic,
		'tags': tags,
		'vote': vote,
		'emoti': emoti
	}

	return scrape

def parse_tags(tags):
	if tags is None: return []
	tags = tags.text().split('\n') # This will also include empty elements
	return tags


def extract_emotions(emoti_str):
	__emotions = ['ขำกลิ้ง','สยอง','ถูกใจ','ทึ่ง']
	emotions = [(e,emoti_str.count(e))  for e in __emotions]
	return emotions