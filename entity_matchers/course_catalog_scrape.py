import requests
import re
from lxml import html
from NameResolver import *
from Writers import *

class CourseInfo:

	A_HREF_TEXT = './a[@href]/text()'
	A_HREF_HREF = './a[@href]/@href'
	TD = './td'
	TEXT = './text()'

	INSTRUCTOR_SEPARATOR = '[,]? ?[,/&]+ ?'
	DAY_OF_THE_WEEK = '[MTuWF]+[h]?'
	TIME_OF_DAY = '[-0-9:]+'
	PROGRAMMING_LANGUAGE_USED = '["][a-zA-Z]+["]'

	def __init__(self, c, PAGE, nameRes):
		self.dept = None
		self.primary_course_id = None
		self.secondary_course_id = None
		self.course_website = None
		self.course_name = None
		self.offering_detail = []
		tds = c.xpath(CourseInfo.TD)

		# course_id
		course_id = re.split(' ?[,] ?', re.sub('EECS', '', tds[0].xpath(CourseInfo.A_HREF_TEXT)[0]))
		course = re.split(' ', course_id[0])
		if len(course) == 1:
			self.primary_course_id = course_id[0]
			if len(course_id) > 1:
				self.secondary_course_id = course_id[1]
			else:
				self.secondary_course_id = ''
			self.dept = 'EECS'
		else:
			self.primary_course_id = course[1]
			self.secondary_course_id = ''
			self.dept = course[0]

		# website
		self.course_website = PAGE + tds[0].xpath(CourseInfo.A_HREF_HREF)[0]

		# course name
		self.course_name = tds[1].xpath(CourseInfo.A_HREF_TEXT)[0]

		# course meeting times and instructors
		for i in range(2,5):
			a = tds[i].xpath(CourseInfo.TEXT)
			if len(a) == 0:
				self.offering_detail.append([])
			elif len(a) == 1:
				lis = re.split('[ ;]+', a[0].strip())
				self.offering_detail.append([[lis[2]], [[lis[1], lis[0]]]])
			else:
				handle = []

				# instructor resolution
				instructor = re.split(CourseInfo.INSTRUCTOR_SEPARATOR, a[1].strip())
				insts = []
				for inst in instructor:
					entities = nameRes.getEntity(inst)
					inst_res = map(lambda x: x.getFullName(), entities)
					if len(inst_res) == 0:
						inst_res.append(inst)
					insts.extend(inst_res)
				handle.append(insts)

				# time resolution
				if 'TBA' in a[0]:
					handle.append([[a[0],'']])
				else:
					lis = re.split('[&,]', a[0])
					if len(lis) > 1:
						d1 = re.findall(CourseInfo.DAY_OF_THE_WEEK,lis[0])
						t1 = re.findall(CourseInfo.TIME_OF_DAY,lis[0])
						d2 = re.findall(CourseInfo.DAY_OF_THE_WEEK,lis[1])
						t2 = re.findall(CourseInfo.TIME_OF_DAY,lis[1])
						d2.extend(t2)
						if len(d1) == 0:
							d1.append(d2[0])
						d1.extend(t1)	
						if len(t2) > 0:	
							handle.append([d1, d2])
						else:
							handle.append([d1])
					else:
						d1 = re.findall(CourseInfo.DAY_OF_THE_WEEK,lis[0])
						t1 = re.findall(CourseInfo.TIME_OF_DAY,lis[0])
						d1.extend(t1)
						handle.append([d1])

				# appendix info resolution
				appendix = re.findall(CourseInfo.PROGRAMMING_LANGUAGE_USED,a[0])
				if len(appendix) > 0:
					handle.append(appendix[0][1:-1])
				self.offering_detail.append(handle)
	def printContent(self):
		w = JSONWriter()
		w.start()
		w.entry('dept',self.dept)
		w.header('class_no')
		w.startCluster()
		w.text(self.primary_course_id)
		if len(self.secondary_course_id) > 0:
			w.text(self.secondary_course_id)
		w.endCluster()
		w.entry('course_description_link',self.course_website)
		w.entry('course_title',self.course_name)
		seasons = ['fall_schedule', 'winter_schedule', 'spring_schedule']
		for i in range(0,3):
			season = self.offering_detail[i]
			w.header(seasons[i])
			w.start()
			if len(season) > 0:
				w.header('instructors')
				w.startCluster()
				for inst in season[0]:
					w.text(inst)
				w.endCluster()
				w.header('schedule')
				w.startCluster()
				for slot in season[1]:
					w.start()
					w.entry('days',slot[0])
					if slot[0] != 'TBA':
						w.entry('hours',slot[1])
					w.end()
				w.endCluster()
				if len(season) > 2:
					w.entry('comment', season[2])
			w.end()
		w.end()
		print w.output()
		# print [self.dept, self.primary_course_id, self.secondary_course_id, self.course_website, self.course_name] + self.offering_detail

class CourseCatalog:

	PAGE = 'https://www.mccormick.northwestern.edu/eecs/courses/'
	CATALOG_TABLE = '//table[@class="table-no-auto-resize" and @id="course_list"]'
	CATALOG_TABLE_HEAD_ENTRY = './thead/tr/th/text()'
	TBODY_TR = './tbody/tr'

	def __init__(self):
		self.courses = []
		self.logger = SimpleLogger()
		self.nameRes = NameResolver(self.logger)

		""" debug only """
		# root_page_content = None
		# with open('./eecs_catalog.html', 'r') as content_file:
		# 	root_page_content = content_file.read()
		# root = html.fromstring(root_page_content)

		""" non-debug test run """
		root = html.fromstring(requests.get(CourseCatalog.PAGE).content)

		""" scrape """
		table = root.xpath(CourseCatalog.CATALOG_TABLE)
		table_title = table[0].xpath(CourseCatalog.CATALOG_TABLE_HEAD_ENTRY)
		all_courses = table[0].xpath(CourseCatalog.TBODY_TR)
		for c in all_courses:
			self.addCourse(CourseInfo(c, CourseCatalog.PAGE, self.nameRes))
	def addCourse(self, ci):
		if ci.course_name != 'TBA':
			self.courses.append(ci)
	def printAll(self):
		for c in self.courses:
			c.printContent()


def __main__():
	CourseCatalog().printAll()

if __name__ == '__main__':
	__main__()
