from course_catalog_scrape import *
from ManualScrapers import *

import re

# https://stackoverflow.com/questions/2460177/edit-distance-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


class CourseResolver:
	def __init__(self):
		self.cc = CourseCatalog()
		self.ugms = UndergraduateManualScraper()
		self.ugms.conv_ee()
		self.ugms.conv_ce()	
		self.ugms.conv_cs()
		self.fn = NameResolver(SimpleLogger(), 'name_resolver.jl')
	def resolve(self):
		out = []
		no_instr = []
		no_match = []
		for key in self.cc.courses_map:
			cc_course = self.cc.courses_map[key]
			for c1 in cc_course:
				discipline_set = Set()
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
					out.append(c1.primary_course_id + ' ' + c1.course_name + ' ' + str(list(discipline_set)))
					c1.disciplines.extend(list(discipline_set))
				else:
					# print c1
					instructorSet = Set()
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
							no_match.append(key+ ' ' + c1.course_name + ' ' + str(list(instructorSet)))
							# print '--- Cannot match instructor: ', c1, '; candidates: ', list(instructorSet)
						else:
							c1.disciplines.extend(list(discipline_set))
							out.append(key+ ' ' + c1.course_name + ' ' + str(list(discipline_set)))
					else:
						no_instr.append(key+ ' ' + c1.course_name)
		out.sort()
		no_instr.sort()
		no_match.sort()
		# print 
		# print "Matches"
		# print
		# for i in out:
		# 	print i
		# print 
		# print "No Match"
		# print
		# for i in no_match:
		# 	print i
		# print 
		# print "No Instructor"
		# print
		# for i in no_instr:
		# 	print i


def __main__():
	cr = CourseResolver()
	cr.resolve()
	print '(in-microtheory CoursesMt)'
	print 
	for i in cr.cc.courses_map:
		for j in cr.cc.courses_map[i]:
			print j
			n = re.sub('[ &]+' ,'', j.course_name)
			print '(isa %s EECSCourse)' % (n)
			print '(primaryCourseID %s "%s")' % (n, j.primary_course_id)
			print '(courseName %s "%s")' % (n, j.course_name)
			for dis in j.disciplines:
				dis = re.sub('[ ]+' ,'', dis)
				print '(courseDiscipline %s %s)' % (n, dis)
			if len(j.offering_detail[0]) > 0:
				print '(courseFallOffering %s)' % (n)
				for fac in j.offering_detail[0][0]:
					fac = re.sub('[ .&]+' ,'', str(fac))
					print '(instructorOfCourseFn (CourseFallOffering %s) %s)' % (n, fac)
				for time in j.offering_detail[0][1]:
					print '(timeOfCourseFn (courseFallOffering %s) (courseTime "%s" "%s")' % (n, time[0], time[1])
			if len(j.offering_detail[1]) > 0:
				print '(courseWinterOffering %s)' % (n)
				for fac in j.offering_detail[1][0]:
					fac = re.sub('[ .&]+' ,'', str(fac))
					print '(instructorOfCourseFn (courseWinterOffering %s) %s)' % (n, fac)
				for time in j.offering_detail[1][1]:
					print '(timeOfCourseFn (courseWinterOffering %s) (courseTime "%s" "%s")' % (n, time[0], time[1])
			if len(j.offering_detail[2]) > 0:
				print '(courseSpringOffering %s)' % (n)
				for fac in j.offering_detail[2][0]:
					fac = re.sub('[ .&]+' ,'', str(fac))
					print '(instructorOfCourseFn (courseSpringOffering %s) %s)' % (n, fac)
				for time in j.offering_detail[2][1]:
					print '(timeOfCourseFn (courseSpringOffering %s) (courseTime "%s" "%s"))' % (n, time[0], time[1])
			print



if __name__ == '__main__':
	__main__()