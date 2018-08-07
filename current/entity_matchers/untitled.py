import re
import requests
from lxml import html
import json

academic_group_request_url = 'https://www.mccormick.northwestern.edu/eecs/people/faculty/service.php?research_area='
academic_groups = {'SolidStateAndPhotonics':'Solid%20State%20and%20Photonics',
					'SignalsAndSystems':'Signals%20and%20Systems',
					'ComputerEngineeringAndSystems':'Computer%20Engineering%20and%20Systems',
					'ComputingAlgorithmsAndApplications':'Computing%20Algorithms%20and%20Applications',
					'CognitiveSystems':'Cognitive%20Systems',
					'GraphicsAndInteractiveMedia':'Graphics%20and%20Interactive%20Media'}

def query_service_php_for_json(url):
	all_info = requests.get(url).content
	all_info = re.sub('[\\\]', '', all_info)
	all_info = re.sub('[ ][ ]', ' ', all_info)
	all_info = re.sub('[(] ?at ?[)]', '@', all_info)
	return json.loads(all_info)['results']


# query_service_php_for_json()
for key, val in academic_groups.items():
	print('%s, %s' % (key, val))