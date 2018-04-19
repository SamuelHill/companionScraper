# Requires Python 2.x
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# pip install lxml
# pip install requests

from lxml import html
import requests

page = requests.get('http://www.mccormick.northwestern.edu/eecs/people/faculty/')
tree = html.fromstring(page.content)

# Getting everyone's email address
try0 = tree.xpath('//div[@class="faculty"]')
output = '{'
first = True
for x in try0:
	try1 = x.xpath('./div[@class="faculty-info"]/h3/a[ @href]/text()')
	try2 = x.xpath('./div[@class="faculty-info"]//a[@class="mail_link" and @href]/@href')
	if first:
		first = False
	else:
		output += ','
	output += '{"name":"%s","email":"%s"}' % (try1[0], try2[0][7:])
output += '}'

print output
