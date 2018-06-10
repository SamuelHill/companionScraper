# -*- coding: utf-8 -*-
from lxml import html
import requests

PARTIAL  = 'https://www.4icu.org/reviews/index'
all_colleges = []
for page in [PARTIAL + str(i) + '.htm' for i in xrange(28)]:
	tree = html.fromstring(requests.get(page).content)
	for college in tree.xpath('//tbody/tr/td/a[@href]/text()'):
		all_colleges.append(college)
		print college