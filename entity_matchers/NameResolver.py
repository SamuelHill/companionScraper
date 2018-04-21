import re
import requests
from lxml import html

class SimpleLogger:
	def __init__(self):
		self.priority = []
		self.entries = []
	def log(self, threeHighOneLow, texts):
		self.priority.append(threeHighOneLow)
		self.entries.append(texts)
	def printAll(self):
		for i in range(0, len(self.priority)):
			if self.priority[i] == 1:
				print '[INFO]',self.entries[i]
			elif self.priority[i] == 2:
				print '[WARNING]',self.entries[i]
			elif self.priority[i] == 3:
				print '[FAILURE]',self.entries[i]

class NameEntry:
	def __init__(self, name):
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


class NameResolver:
	
	PAGE = 'http://www.mccormick.northwestern.edu/eecs/people/faculty/'
	FACULTY = '//div[@class="faculty"]'
	FAC_BLOCK = './div[@class="faculty-info"]/h3/a[ @href]'
	TEXT = './text()'

	def __init__(self, logger):
		self.lastNameDict = {}
		self.logger = logger

		# Getting everyone's name
		faculties = html.fromstring(requests.get(NameResolver.PAGE).content).xpath(NameResolver.FACULTY)
		for x in faculties:
			name = x.xpath(NameResolver.FAC_BLOCK)[0].xpath(NameResolver.TEXT)[0]
			self.addEntity(NameEntry(name))
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
	def printAllEntities(self):
		for key, value in self.lastNameDict.iteritems() :
			for e in value:
				print e


def main():
	logger = SimpleLogger()
	r = NameResolver(logger)
	r.printAllEntities()
	# r.printLogs()

if __name__== "__main__":
	main()