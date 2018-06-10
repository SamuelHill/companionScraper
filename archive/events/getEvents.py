# -*- coding: utf-8 -*-
from lxml import html
import requests
import string

# IDENTIFIERS FOR NAVIGATING PAGE:
PAGE = 'https://planitpurple.northwestern.edu'
# list of events, can get href to event detail page
EVENTS_LIST = '//ul[@class="events"]/li/a/@href'
# attributes to look for on event details page
EVENT_NAME         = '//div[@class="event_header"]/h2/text()'
EVENT_DATE_MONTH   = '//div[@class="event_date"]/div[@class="month"]/text()'
EVENT_DATE_DAY     = '//div[@class="event_date"]/div[@class="day"]/text()'
EVENT_DATE_TIME    = '//div[@class="event_date"]/div[@class="time"]/text()'
EVENT_DATE_WEEKDAY = '//div[@class="event_date"]/div[@class="time"]/span/text()'
RECURRING          = '//p[@id="recurring"]'
AUDIENCE_TEXT      = '//span[text()[contains(.,"Audience")]]/../text()'
CATEGORY_TEXT      = '//span[contains(@class, "event_category")]/text()'
CONTACT_TEXT       = '//span[text()[contains(.,"Contact")]]/../text()'
WHERE_TEXT         = '//span[text()[contains(.,"Where")]]/../text()'
GROUP_TEXT         = '//span[text()[contains(.,"Group")]]/../a/text()'
WHEN_TEXT          = '//span[text()[contains(.,"When")]]/../text()'
COST_TEXT          = '//span[text()[contains(.,"Cost")]]/../text()'
# general tags
TEXT = './text()'
HREF = './@href'


# helper func, clean text
def xpathToCleanString(source, xpath_text):
	xpath_list = source.xpath(xpath_text)
	if xpath_list:
		table = string.maketrans("", "")
		utf8_safe = " ".join(xpath_list).encode('utf-8')
		no_tab_newline = utf8_safe.translate(table, "\t\n").strip()
		return no_tab_newline
	return None


# helper func, check if content exists
def xpathToBoolContentExists(source, xpath_text):
	return False if source.xpath(xpath_text) == [] else True


# helper func, prepare unique name
def uniqueEventName(event_data):
	clean_name = event_data['event_name'].translate(None, string.punctuation)
	clean_name.replace('’', '')
	clean_date = event_data['date_time'].translate(None, string.punctuation)
	return "".join(clean_name.split()) + "".join(clean_date.split())


# SCRAPE:
# get base event listing website
htmlContent = requests.get(PAGE).content
mainTree = html.fromstring(htmlContent)
# grab events from page as list,
events = mainTree.xpath(EVENTS_LIST)
# loop over every event on this page and collect scraped event data
all_event_data = []
for event in events:
	# setup event data for each event
	event_data = dict.fromkeys(['event_name', 'month', 'day', 'time',
								'day_of_week', 'recurring', 'location',
								'audience', 'category', 'contact', 'group',
								'cost', 'date_time', 'unique_ID'], None)
	# go to specific event detail page
	content = requests.get(PAGE + event).content
	tree = html.fromstring(content)
	# scrape event data
	event_data['event_name']  = xpathToCleanString(tree, EVENT_NAME)
	event_data['month']       = xpathToCleanString(tree, EVENT_DATE_MONTH)
	event_data['day']         = xpathToCleanString(tree, EVENT_DATE_DAY)
	event_data['time']        = xpathToCleanString(tree, EVENT_DATE_TIME)
	event_data['day_of_week'] = xpathToCleanString(tree, EVENT_DATE_WEEKDAY)
	event_data['recurring']   = xpathToBoolContentExists(tree, RECURRING)
	event_data['date_time']   = xpathToCleanString(tree, WHEN_TEXT)
	event_data['location']    = xpathToCleanString(tree, WHERE_TEXT)
	event_data['audience']    = xpathToCleanString(tree, AUDIENCE_TEXT)
	event_data['category']    = xpathToCleanString(tree, CATEGORY_TEXT)
	event_data['contact']     = xpathToCleanString(tree, CONTACT_TEXT)
	event_data['group']       = xpathToCleanString(tree, GROUP_TEXT)
	event_data['cost']        = xpathToCleanString(tree, COST_TEXT)
	event_data['unique_ID']   = uniqueEventName(event_data)
	# collect all event data
	all_event_data.append(event_data)


# MELD PROCESSING:
for event_data in all_event_data:
	print "(isa " + event_data['unique_ID'] + " NUEvent)"
	quoted_name = " \"" + event_data['event_name'] + "\""
	print "(eventName " + event_data['unique_ID'] + quoted_name + ")"
	if event_data['location']:
		quoted_loc = " \"" + event_data['location'] + "\""
		print "(eventLocale " + event_data['unique_ID'] + quoted_loc + ")"
	quoted_date = " \"" + event_data['date_time'] + "\""
	print "(dateOfEvent " + event_data['unique_ID'] + quoted_date + ")"
	print ''
