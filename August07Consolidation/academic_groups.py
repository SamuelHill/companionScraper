import re
import requests
from lxml import html
import json
from io import StringIO

class AcademicGroupResolver:

	academic_group_request_url = 'https://www.mccormick.northwestern.edu/eecs/people/faculty/service.php?research_area='
	academic_groups = {'NUSolidStateAndPhotonics':'Solid%20State%20and%20Photonics',
						'NUSignalsAndSystems':'Signals%20and%20Systems',
						'NUComputerEngineeringAndSystems':'Computer%20Engineering%20and%20Systems',
						'NUComputingAlgorithmsAndApplications':'Computing%20Algorithms%20and%20Applications',
						'NUCognitiveSystems':'Cognitive%20Systems',
						'NUGraphicsAndInteractiveMedia':'Graphics%20and%20Interactive%20Media'}
	faculty_and_affiliations = {}

	def __init__(self):
		self.sio = StringIO()
		return
	def query_service_php_for_json(string, url):
		all_info = requests.get(url).content.decode('utf-8')
		all_info = re.sub('[\\\\]', '', all_info)
		all_info = re.sub('[ ][ ]', ' ', all_info)
		all_info = re.sub('[(] ?at ?[)]', '@', all_info)
		return json.loads(all_info)['results']

	def formatName(self, string):
		return re.sub('[ .]+','',string)

	def w(self, txt):
		self.sio.write(txt+'\n')

	def pull(self):
		for key, val in AcademicGroupResolver.academic_groups.items():
			nameArr = self.query_service_php_for_json(AcademicGroupResolver.academic_group_request_url + val)
			for e in nameArr:
				name = self.formatName(e['full_name'])
				if name not in AcademicGroupResolver.faculty_and_affiliations:
					AcademicGroupResolver.faculty_and_affiliations[name] = []
				AcademicGroupResolver.faculty_and_affiliations[name].append(key)
		for name, groups in AcademicGroupResolver.faculty_and_affiliations.items():
			self.w(str.format("\n(in-microtheory (SocialModelMtFn %s))" % (name)))
			for g in groups:
				self.w(str.format("(nuGroupMember %s %s)" % (g, name)))
		return self.sio.getvalue()

def __main__():
	print(AcademicGroupResolver().pull())
	

if __name__ == '__main__':
	__main__()