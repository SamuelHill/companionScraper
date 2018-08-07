from course_catalog_scrape import *
from ManualScrapers import *

import re

# https://stackoverflow.com/questions/2460177/edit-distance-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = list(range(len(s1) + 1))
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

class crc:
	name_resolver_path = './intermediate_results/name_resolver.jl'

class CourseResolver:
	def __init__(self):
		self.cc = CourseCatalog()
		self.ugms = UndergraduateManualScraper()
		self.ugms.convert_all_disciplines()
		self.fn = NameResolver(SimpleLogger(), crc.name_resolver_path)
		self.out = []
		self.no_instr = []
		self.no_match = []
		self.buffer = StringIO()
	def resolve(self):
		for key in self.cc.courses_map:
			cc_course = self.cc.courses_map[key]
			for c1 in cc_course:
				discipline_set = set()
				# resolve with direct manual listing
				if key in self.ugms.mapping:
					# print key 
					if (key != '395' and key != '396' and key != '397'):
						for ugc in self.ugms.mapping[key]:
							discipline_set.add(ugc.discipline)
					else:
						for ugc in self.ugms.mapping[key]:
							if (key != '395' and key != '396' and key != '397') and ugc.course_name == c1.course_name:
								discipline_set.add(ugc.discipline)
				# resolve with faculty name
				if len(discipline_set) > 0:
					self.out.append(c1.primary_course_id + ' ' + c1.course_name + ' ' + str(list(discipline_set)))
					c1.disciplines.extend(list(discipline_set))
				else:
					# print c1
					instructorSet = set()
					for i in range(0,3):
						seasons = c1.offering_detail[i]
						if len(seasons) > 0:
							for instructor in seasons[0]:
								instructorSet.add(str(instructor))
					if len(instructorSet) > 0:
						for fac in instructorSet:
							last = re.search('[-a-zA-Z]+$', fac).group()
							# print last
							if last in self.fn.lastNameDict:
								for i in self.fn.lastNameDict[last][0].divisions:
									discipline_set.add(i)
							elif last in self.fn.fullNameDict:
								for i in self.fn.fullNameDict[fac][0].divisions:
									discipline_set.add(i)
						if len(discipline_set) == 0:
							self.no_match.append(key+ ' ' + c1.course_name + ' ' + str(list(instructorSet)))
							# print '--- Cannot match instructor: ', c1, '; candidates: ', list(instructorSet)
						else:
							c1.disciplines.extend(list(discipline_set))
							self.out.append(key+ ' ' + c1.course_name + ' ' + str(list(discipline_set)))
					else:
						self.no_instr.append(key+ ' ' + c1.course_name)
		self.out.sort()
		self.no_instr.sort()
		self.no_match.sort()
		return self
	def w(self, txt):
		self.buffer.write(txt+'\n')
	def addIndexedProperName(self, course_name_used, represetnatationToken):
		stuff = re.split(' ', course_name_used)
		if stuff[0] != course_name_used:
			if stuff[0] == 'An':
				stuff = stuff[1:]
			self.w(str.format('(indexedProperName (TheList %s) %s %s)' %  (str.join(' ', stuff[0:-1]), stuff[-1], represetnatationToken)))
			if stuff[0] == 'Introduction':
				self.w(str.format('(indexedProperName (TheList Intro %s) %s %s)' %  (str.join(' ', stuff[1:-1]), stuff[-1], represetnatationToken)))
	def ontologize(self):
		self.opened_file = StringIO()
		self.w('(in-microtheory NUCoursesMt)')
		self.w('(genlMt SocialModelingMt NUCoursesMt)')
		self.w('') 

		timeOfCourseFn = '(timeOfCourseFn (courseSpringOffering %s) (courseTime "%s" "%s"))'

		for i in self.cc.courses_map:
			for j in self.cc.courses_map[i]:
				# self.w(str.formatj)
				course_name_used = re.sub('&' ,'And', j.course_name)
				course_name_used = re.sub(',' ,'', course_name_used)
				course_name_used = course_name_used.split(':')[0]
				n = re.sub('[ ,]+' ,'', course_name_used)
				self.w(str.format('(isa %s EECSCourse)' % (n)))
				self.w(str.format('(primaryCourseID %s "%s")' % (n, j.primary_course_id)))
				self.w(str.format('(courseName %s "%s")' % (n, course_name_used)))
				for dis in j.disciplines:
					dis = re.sub('[ ]+' ,'', dis)
					self.w(str.format('(courseDiscipline %s %s)' % (n, dis)))
				if len(j.offering_detail[0]) > 0:
					self.w(str.format('(courseFallOffering %s)' % (n)))
					for fac in j.offering_detail[0][0]:
						fac = re.sub('[ .&]+' ,'', str(fac))
						self.w(str.format('(instructorOfCourseFn (CourseFallOffering %s) %s)' % (n, fac)))
					for time in j.offering_detail[0][1]:
						self.w(str.format('(timeOfCourseFn (courseFallOffering %s) (courseTime "%s" "%s")' % (n, time[0], time[1])))
				if len(j.offering_detail[1]) > 0:
					self.w(str.format('(courseWinterOffering %s)' % (n)))
					for fac in j.offering_detail[1][0]:
						fac = re.sub('[ .&]+' ,'', str(fac))
						self.w(str.format('(instructorOfCourseFn (courseWinterOffering %s) %s)' % (n, fac)))
					for time in j.offering_detail[1][1]:
						self.w(str.format('(timeOfCourseFn (courseWinterOffering %s) (courseTime "%s" "%s")' % (n, time[0], time[1])))
				if len(j.offering_detail[2]) > 0:
					self.w(str.format('(courseSpringOffering %s)' % (n)))
					for fac in j.offering_detail[2][0]:
						fac = re.sub('[ .&]+' ,'', str(fac))
						self.w(str.format('(instructorOfCourseFn (courseSpringOffering %s) %s)' % (n, fac)))
					for time in j.offering_detail[2][1]:
						self.w(str.format(timeOfCourseFn % (n, time[0], time[1])))
				self.addIndexedProperName(course_name_used, n)
				self.w('')
		return self.buffer.getvalue()


def __main__():
	print(CourseResolver().resolve().ontologize())


if __name__ == '__main__':
	__main__()