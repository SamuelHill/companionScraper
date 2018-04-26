import re
import requests
from lxml import html
import json

class SimpleLogger:
	def __init__(self):
		self.priority = []
		self.entries = []
	def log(self, threeHighOneLow, texts):
		self.priority.append(threeHighOneLow)
		self.entries.append(texts)
	def printAll(self):
		if len(self.entries) == 0:
			print '[REPORT] Log is empty.'
			return
		for i in range(0, len(self.priority)):
			if self.priority[i] == 1:
				print '[INFO]',self.entries[i]
			elif self.priority[i] == 2:
				print '[WARNING]',self.entries[i]
			elif self.priority[i] == 3:
				print '[FAILURE]',self.entries[i]

class NameEntry:
	def __init__(self, name, divisions=[], first='', last='', middles='', nicks=''):
		self.divisions = divisions
		if first == '' and last == '':
			sp = name.title().split()
			l = len(sp)
			self.nickNames = []
			middle = []
			if l == 1:
				self.first = name
				self.last = ''
			else:
				self.first = sp[0]
				self.last = sp[-1]
				middle = sp[1:-1]
			self.middleNames = []
			self.middleNamesAbbrs = []
			if len(middle) > 0:
				for m in middle:
					if '(' in m:
						mrp = re.sub('[()]', '', m)
						self.nickNames += [mrp]
					elif '.' in m:
						self.middleNames += [m]
						self.middleNamesAbbrs += [m]
					else:
						self.middleNames += [m]
						self.middleNamesAbbrs += [m[0] + '.']
			if '-' in self.first:
				self.first_split = self.first.split('-')
			else:
				self.first_split = [self.first]
		else:
			self.first = first
			self.last = last
			self.middleNames = middles
			self.nickNames = nicks
			self.middleNamesAbbrs = []
			if len(middles) > 0:
				for m in middles:
					if '.' in m:
						self.middleNamesAbbrs += [m]
					else:
						self.middleNamesAbbrs += [m[0] + '.']
			if '-' in first:
				self.first_split = first.split('-')
			else:
				self.first_split = [first]
	def __str__(self):
		return self.getFullName()
	def __repr__(self):
		return self.getFullName()
	def isMatchLastName(self, ln):
		return self.last == ln
	def getFullName(self):
		return ' '.join([self.first] + self.middleNames + [self.last])
	def getNickNames(self):
		return self.nickNames
	def getMiddleNameAbbrsWithDots(self):
		return ' '.join(map(lambda x : x[0] + '.', self.middleNamesAbbrs))
	def getFirstNameAbbrDots(self):
		return '.'.join(map(lambda x : x[0], self.first.split('-'))) + '.'
	def getFirstNameAbbrDash(self):
		return '-'.join(map(lambda x : x[0], self.first.split('-')))
	def getFirstNameAbbrNoSpace(self):
		return ''.join(map(lambda x : x[0], self.first.split('-')))


def as_name_entry(dict):
	return NameEntry('', map(lambda x : str(x), dict['divisions']), str(dict['first_name']), str(dict['last_name']), map(lambda x : str(x), dict['middle_names']), map(lambda x : str(x), dict['nick_names']))

class NameResolver:
	
	ALL_FACULTIES = 'http://www.mccormick.northwestern.edu/eecs/people/faculty/service.php?academic_division=*'

	def __init__(self, logger, path = ''):
		self.lastNameDict = {}
		self.logger = logger

		# Getting everyone's name
		if path == '':
			all_faculties = NameResolver.query_service_php_for_json(NameResolver.ALL_FACULTIES)
			for x in all_faculties:
				divs = re.split(' ?[|] ?', str(x['all_divisions']))
				self.addEntity(NameEntry( x['full_name'], [] if divs[0] == '' else divs))
		else:
			with open(path, 'r') as content_file:
				json_line = content_file.readline()
				while json_line:
					entry = json.loads(json_line, object_hook=as_name_entry)
					self.addEntity(entry)
					json_line = content_file.readline()
	def printLogs(self):
		self.logger.printAll()
	def addEntity(self, nameEntry):
		if nameEntry.last in self.lastNameDict:
			self.lastNameDict[nameEntry.last] += [nameEntry]
		else:
			self.lastNameDict[nameEntry.last] = [nameEntry]
	def getEntitiesByLastName(self, lastName):
		return self.lastNameDict[lastName.title()]
	def getEntity(self, nameString):
		sp = re.split('[. -]+', nameString.title())
		last = sp[-1]
		if last in self.lastNameDict:
			el = self.lastNameDict[last]
		else:
			return []
		out = []
		if len(sp) > 1:
			# deal with first name cases
			for e in el:
				firstMatch = False
				middleMatch = False	
				if len(sp) > 2:
					if e.getMiddleNameAbbrsWithDots() == ' '.join(
						map(lambda x: x[0] + '.', sp[1:-1])):
							middleMatch = True
				elif len(sp) == 2:
					middleMatch = True
				if e.first == sp[0]:
					firstMatch = True
				elif '.' in e.first or e.getFirstNameAbbrDots() == sp[0]:
					firstMatch = True
				elif '-' in e.first or e.getFirstNameAbbrDash() == sp[0]:
					# C-H Lee
					firstMatch = True
				elif sp[0] in e.nickNames:
					firstMatch = True
				else:
					self.logger.log(2, 'Cannot parse first entry in name string: ' + sp[0])
				if firstMatch is True and middleMatch is True:
					out.append(e)
		elif len(sp) == 1:
			for e in el:
				if e.last == sp[0]:
					out.append(e)
				elif '-' in e and e.getFirstNameAbbrNoSpace()+e.lastName == sp[0]:
					out.append(e)
				else:
					self.logger.log(2, 'Cannot parse namestring: ' + sp[0])
		return out
	@staticmethod
	def query_service_php_for_json(url):
		all_info = requests.get(url).content
		all_info = re.sub('[\\\]', '', all_info)
		all_info = re.sub('[ ][ ]', ' ', all_info)
		all_info = re.sub('[(] ?at ?[)]', '@', all_info)
		return json.loads(all_info)['results']
	@staticmethod
	def formJSONListStr(list_to_form):
		return '[]' if len(list_to_form) == 0 else ('["'+ '","'.join(list_to_form) + '"]')
	def printAllEntities(self):
		for key, value in self.lastNameDict.iteritems() :
			for e in value:
				print '{"full_name":"%s","last_name":"%s","first_name":"%s","middle_names":%s,"nick_names":%s,"divisions":%s}' % (e, e.last, e.first, NameResolver.formJSONListStr(e.middleNames),NameResolver.formJSONListStr(e.nickNames),NameResolver.formJSONListStr(e.divisions))



def main():
	logger = SimpleLogger()
	r = NameResolver(logger, 'name_resolver.jl')
	r.printAllEntities()
	r.printLogs()

if __name__== "__main__":
	main()