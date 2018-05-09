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

class crc:
	name_resolver_path = './results/name_resolver.jl'

class CourseResolver:
	def __init__(self):
		self.cc = CourseCatalog()
		self.ugms = UndergraduateManualScraper()
		self.ugms.convert_all_disciplines()
		self.fn = NameResolver(SimpleLogger(), crc.name_resolver_path)
		self.out = []
		self.no_instr = []
		self.no_match = []
	def resolve(self):
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
					self.out.append(c1.primary_course_id + ' ' + c1.course_name + ' ' + str(list(discipline_set)))
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
	def ontologize(self):
		print '(in-microtheory ClassesForSocialModelingMt)'
		print '(genlMt ClassesForSocialModelingMt SocialModelingMt)'
		print '(genlMt SocialModelingMt ClassesForSocialModelingMt)'
		print 
		print ';;; //\\\\//\\\\//\\\\// Collections \\\\//\\\\//\\\\//\\\\'
		print 
		print '(isa NUCourse Collection)'
		print '(genls NUCourse Course-Collegiate)'
		print '(comment NUCourse "NUCourse is an course offered at Northwestern University")'
		print 
		print '(isa NUCourse-EECS Collection)'
		print '(genls NUCourse-EECS NUCourse)'
		print '(comment NUCourse-EECS "NUCourse-EECS is an EECS course offered at Northwestern University")'
		print
		print '(isa NUCourse-CS Collection)'
		print '(genls NUCourse-CS NUCourse)'
		print '(comment NUCourse-CS "NUCourse-CS is an Computer Science (CS) course offered at Northwestern University")'
		print
		print '(isa NUCourse-CE Collection)'
		print '(genls NUCourse-CE NUCourse)'
		print '(comment NUCourse-CE "NUCourse-CE is an Computer Engineering (CE) course offered at Northwestern University")'
		print
		print '(isa NUCourse-EE Collection)'
		print '(genls NUCourse-EE NUCourse)'
		print '(comment NUCourse-EE "NUCourse-EE is an Electrical Engineering (EE) course offered at Northwestern University")'
		print
		print '(isa primaryCourseID Collection)'
		print '(isa secondaryCourseID Collection)'
		print '(genls primaryCourseID identification)'
		print '(genls secondaryCourseID identification)'
		print
		print ';;; //\\\\//\\\\//\\\\// Predicates \\\\//\\\\//\\\\//\\\\'
		print '(isa courseName Predicate)'
		print '(genlPreds courseName nameString)'
		print '(arity courseName 2)'
		print '(arg1Isa courseName  Course-Collegiate)'
		print '(arg2Isa courseName  ProperNameString)'
		print '(comment courseName  "(courseName ?course ?ProperNameString) a ?course has name ?Name")'
		print 
		# ;;; Cannot find an appropriate term. Tried 
		# ;;; Semester, quarter, term. 
		print '(isa SchoolTerm SeasonOfYear)'
		print '(isa springQuarter-SchoolTerm SchoolTerm)'
		print '(isa fallQuarter-SchoolTerm SchoolTerm)'
		print '(isa winterQuarter-SchoolTerm SchoolTerm)'
		print 
		print '(isa teachCourse Predicate)'
		print '(arity teachCourse 3)'
		print '(arg1Isa teachCourse Agent-Generic)'
		print '(arg2Isa teachCourse NUCourse)'
		print '(arg3Isa teachCourse SchoolTerm)'
		print '(comment teachCourse "(teachCourse ?person ?course ?quarter) says that ?person teaches ?course during ?quarter")'
		print 
		print '(isa timeOfCourse Predicate)'
		print '(arity timeOfCourse 4)'
		print '(arg1Isa timeOfCourse NUCourse)'
		print '(arg2Isa timeOfCourse SchoolTerm)'
		print '(arg3Isa timeOfCourse TimeOfWeekType)'
		print '(arg4Isa timeOfCourse UnitOfTime)'
		print '(comment timeOfCourse "(timeOfCourse ?course ?quarter ?timeOfWeek ?periodOfTime) says that ?course is offered during ?quarter on ?timeOfWeek for ?periodOfTime")'
		print


		# (timeOfCourse ProbabilisticGraphicalModels winterQuarter-SchoolTerm Thursday "3:30-4:50")

		teachesCourseDuringQuarter = '(teachCourse %s %s %s)'

		for i in self.cc.courses_map:
			for j in self.cc.courses_map[i]:
				# print j
				n = re.sub('[,+: &]+' ,'', j.course_name)
				print '(isa %s NUCourse-EECS)' % (n)
				print '(primaryCourseID %s "%s")' % (n, j.primary_course_id)
				if j.secondary_course_id is not '':
					print '(secondaryCourseID %s "%s")' % (n, j.secondary_course_id)
				print '(courseName %s "%s")' % (n, j.course_name)
				for dis in j.disciplines:
					# print '(courseDiscipline %s %s)' % (n, dis)
					if dis == 'Electrical Engineering':
						print '(isa %s NUCourse-EE)' % (n)
					elif dis == 'Computer Engineering':
						print '(isa %s NUCourse-CE)' % (n)
					elif dis == 'Computer Science':
						print '(isa %s NUCourse-CS)' % (n)
					else:
						print 'ERROR! discipline not found: %s' % (dis)
						abort()
				if len(j.offering_detail[0]) > 0:
					# print j.offering_detail[0]
					quarter = 'fallQuarter-SchoolTerm'
					for fac in j.offering_detail[0][0]:
						fac = re.sub('[ .&]+' ,'', str(fac))
						print teachesCourseDuringQuarter % (fac, n, quarter)
					for time in j.offering_detail[0][1]:
						self.parseTimeOfCourse(n, quarter, time)
				if len(j.offering_detail[1]) > 0:
					quarter = 'winterQuarter-SchoolTerm'
					for fac in j.offering_detail[1][0]:
						fac = re.sub('[ .&]+' ,'', str(fac))
						print teachesCourseDuringQuarter % (fac, n, quarter)
					for time in j.offering_detail[1][1]:
						self.parseTimeOfCourse(n, quarter, time)
				if len(j.offering_detail[2]) > 0:
					quarter = 'springQuarter-SchoolTerm'
					for fac in j.offering_detail[2][0]:
						fac = re.sub('[ .&]+' ,'', str(fac))
						print teachesCourseDuringQuarter % (fac, n, quarter)
					for time in j.offering_detail[2][1]:
						self.parseTimeOfCourse(n, quarter, time)
						# print timeOfCourseFn % (n, time[0], time[1])
				print
	def parseTimeOfCourse(self, n, quarter, time):
		day = time[0]
		hours = None if len(time) == 1 else time[1]

		g = re.findall('[MWFTS][uha]?', day)
		courseTimePoint = '(MinuteOfHourFn %s (HourFn %s %s)' # Minute, Hour, Friday
		# (IntervalTypeBetweenFn-Inclusive %s %s)
		out = None
		isTBA = False
		for d in g:
			out = '(timeOfCourse ' + n + ' ' + quarter
			dw = {
		        'M': 'Monday',
		        'Tu': 'Tuesday',
		        'W': 'Wednesday',
		        'Th': 'Thursday',
		        'F': 'Friday',
		        'Sa': 'Saturday',
		        'Su': 'Sunday'
		    }.get(d, 'Unknown')
			if hours is not None:
				hours_arr = hours.split('-')
				hour1 = 0
				hour2 = 0
				minute1 = 0
				minute2 = 0
				if len(hours_arr) == 1:
					if not isTBA:
						out += ' "TBA"'
						isTBA = True
					else:
						continue
				else:
					# out += ' (IntervalTypeBetweenFn-Inclusive '
					one = hours_arr[0].split(':')
					hour1 = int(one[0])
					isHour1Afternoon = False
					if hour1 < 8:
						hour1 += 12
						isHour1Afternoon = True
					if len(one) > 1:
						minute1 = int(one[1])
					out += ' (MinuteOfHourFn ' + str(minute1) + ' (HourFn ' + str (hour1) + ' ' + dw + ')) '

					two = hours_arr[1].split(':')
					hour2 = int(two[0])
					if isHour1Afternoon or hour2 < 4:
						hour2 += 12
					if len(two) > 1:
						minute2 = int(two[1])
					
					out += '(MinutesDuration ' + str((hour2 - hour1) * 60 + minute2 - minute1) + ')'
				# print '(timeOfCourse %s %s %s "%s")' % (n, quarter, dw, hours)
			else:
				if not isTBA:
					out += ' "TBA"'
					isTBA = True
				else:
					continue
				# out += ' "TBA"'
			out += ')'
			print out
def __main__():
	cr = CourseResolver()
	cr.resolve()
	cr.ontologize()
	



if __name__ == '__main__':
	__main__()