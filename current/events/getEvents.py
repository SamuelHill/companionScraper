# Requires Python 2.x
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# pip install lxml
# pip install requests

from lxml import html
import requests
import sys

VERBOSE = True if len(sys.argv) > 1 and sys.argv[1] == '1' else False

def printV(string):
	if VERBOSE and string is not None:
		print string

# IDENTIFIERS FOR NAVIGATING PAGES:
PAGE = 'https://planitpurple.northwestern.edu/#search=2018-04-01/0/1/1//week'
PAGE = 'https://planitpurple.northwestern.edu/#search=/0////month'
# GENERAL TAGS
TEXT = './text()'
HREF = './@href'
HTTP = 'http:'

htmlContent = requests.get(PAGE).content
print htmlContent