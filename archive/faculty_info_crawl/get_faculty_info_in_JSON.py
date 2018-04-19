# Requires Python 2.x
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# pip install lxml
# pip install requests

from lxml import html
import requests
from crawler import *
from unidecode import unidecode

def main():
	# debug purpose
	# root_page_content = None
	# with open('./faculty.html', 'r') as content_file:
	# 	root_page_content = content_file.read()
	# tree = html.fromstring(root_page_content)

	root_page = requests.get('http://www.mccormick.northwestern.edu/eecs/people/faculty/')
	tree = html.fromstring(root_page.content)

	# Getting everyone's email address
	try0 = tree.xpath('//div[@class="faculty"]')
	json = ''
	index = 1
	for x in try0:
		node = x.xpath('./div[@class="faculty-info"]/h3/a[ @href]')[0]
		name = node.xpath('./text()')[0]
		newPageURL = 'http:' + node.xpath('./@href')[0]
		if json != '':
			json += '\n'
		json += stepInFacultyPage(index, name, newPageURL)
		index += 1
	output = json if isinstance(json, str) else unidecode(json)
	print output


if __name__== "__main__":
	main()

