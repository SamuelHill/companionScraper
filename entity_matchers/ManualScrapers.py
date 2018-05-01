import urllib
import os.path
from sets import Set

# need to install PDFMiner from https://github.com/euske/pdfminer/, which supports python 2.x

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from unidecode import unidecode 

import re


class ManualCourseInfo:

	def __init__(self, dept, course_id, discipline, course_name):
		self.dept = dept
		self.primary_course_id = course_id[0]
		self.secondary_course_id = None
		if len(course_id) > 1:
			self.secondary_course_id = course_id[1]
		self.discipline = discipline
		self.course_name = course_name
	def __str__(self):
		return 'EECS ' + self.primary_course_id + ' - ' + self.course_name + ' - ' + self.discipline
	def __repr__(self):
		return 'EECS ' + self.primary_course_id + ' - ' + self.course_name + ' - ' + self.discipline


class UndergraduateManualScraper:
	CoursePattern = re.compile('EECS[-, :/0-9]+([(].+[0-9]+[)])?[- ]*')
	ParenthesizedPattern = re.compile('[(].+[)]')
	def __init__(self):
		if not os.path.isfile('./eecs-undergraduate-manual.pdf'):
			urllib.urlretrieve('https://www.mccormick.northwestern.edu/eecs/documents/undergraduate/eecs-undergraduate-manual.pdf', './eecs-undergraduate-manual.pdf')
		elif not os.path.isfile('./ug_manual_text.txt'):
			# self.text = re.sub(r'[^\x00-\x7F]+',' ', self.convert_pdf_to_txt('./eecs-undergraduate-manual.pdf'))
			self.text = self.convert_pdf_to_txt('./eecs-undergraduate-manual.pdf')
			manual = open('./ug_manual_text.txt', 'w')
			manual.write(self.text)
			manual.close()
		else:
			manual = open('./ug_manual_text.txt', 'r')
			self.text = manual.read()
			manual.close()
		self.mapping = {}

	def convert_pdf_to_txt(self, path):
	    rsrcmgr = PDFResourceManager()
	    retstr = StringIO()
	    codec = 'utf-8'
	    laparams = LAParams()
	    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
	    fp = file(path, 'rb')
	    interpreter = PDFPageInterpreter(rsrcmgr, device)
	    password = ""
	    maxpages = 0
	    caching = True
	    pagenos=set()
	    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,password=password,caching=caching, check_extractable=True):
	        interpreter.process_page(page)
	    text = retstr.getvalue()

	    fp.close()
	    device.close()
	    retstr.close()
	    return text
	def conv_cs(self):
		l = self.text.splitlines()
		lc = len(l)
		starts = False
		for i in range(0, lc):
			li = l[i]
			if not starts:
				if li.startswith('Students, who have never programmed before, in any language'):
					starts = True
			else:
				if li.startswith('4.5 Project Requirement'):
					starts = False
			if starts:
				found = None
				if li.startswith('EECS', 2):
					found = li[2:]
				elif li.startswith('EECS', 3):
					found = li[3:]
				elif li.startswith('EECS', 4):
					found = li[4:]
				elif li.startswith('EECS', 5):
					found = li[5:]
				elif li.startswith('EECS', 6):
					found = li[6:]
				if found is not None and not found.startswith('EECS Undergraduate Study Manual'):
				    found = re.sub(' +',' ',found)
				    c = self.encodeCourse( found, 'Computer Science')
				    if c.primary_course_id not in self.mapping:
				    	self.mapping[c.primary_course_id] = []
				    self.mapping[c.primary_course_id].append(c)
	def conv_ce(self): 
		l = self.text.splitlines()
		lc = len(l)
		starts = False
		for i in range(0, lc):
			li = l[i]
			if not starts:
				if li.startswith('Our curriculum is continuously revised based on feedback from our constituents, e'):
					starts = True
			else:
				if li.startswith('Among the 16 departmental courses, the P/N option may only'):
					starts = False
			if starts:
				found = None
				if li.startswith('EECS') and len(li) > 9:
					found = li
				elif li.startswith('EECS', 2):
					found = li[2:]
				elif li.startswith('EECS', 3):
					found = li[3:]
				elif li.startswith('EECS', 4):
					found = li[4:]
				elif li.startswith('EECS', 5):
					found = li[5:]
				elif li.startswith('EECS', 6):
					found = li[6:]
				if found is not None and not found.startswith('EECS Undergraduate Study Manual'):
					found = re.sub(' +',' ',found)
					c = self.encodeCourse( found, 'Computer Engineering')
					if c.primary_course_id not in self.mapping:
						self.mapping[c.primary_course_id] = []
					self.mapping[c.primary_course_id].append(c)
	def conv_ee(self): 
		l = self.text.splitlines()
		lc = len(l)
		starts = False
		for i in range(0, lc):
			li = l[i]
			if not starts:
				if li.startswith('Systems including Digital Signal Processing'):
					starts = True
			else:
				if li.startswith('Among the 16 departmental courses, the P/N option may only'):
					starts = False
			if starts:
				found = None
				if li.startswith('EECS') and len(li) > 9:
					found = li
				elif li.startswith('EECS', 2):
					found = li[2:]
				elif li.startswith('EECS', 3):
					found = li[3:]
				elif li.startswith('EECS', 4):
					found = li[4:]
				elif li.startswith('EECS', 5):
					found = li[5:]
				elif li.startswith('EECS', 6):
					found = li[6:]
				if found is not None and not found.startswith('EECS Undergraduate Study Manual'):
					found = re.sub(' +',' ',found)
					c = self.encodeCourse( found, 'Electrical Engineering')
					if c.primary_course_id not in self.mapping:
						self.mapping[c.primary_course_id] = []
					self.mapping[c.primary_course_id].append(c)

	def encodeCourse(self, string, discipline): 
		# string = re.sub('\xe2', '', string)
		for i in re.finditer(UndergraduateManualScraper.CoursePattern, string):
			elend = i.end()
			st = re.sub(' - ', '', i.group()[4:])
			st = re.sub('- ', ' ', st)
			st = re.sub(': ?', '', st)
			st = st.strip()
			if ')' in st:
				for stuffr in re.finditer(UndergraduateManualScraper.ParenthesizedPattern, st):
					# print "alternative marking: ", stuffr.group()[1:-1]
					st = st[:stuffr.start()].strip()
			trail = unidecode(unicode(string[elend:], encoding = "utf-8"))
			trail = re.sub('([(].+[)]) *','',trail)
			trail = re.sub('- ','',trail)

			# output = '{"dept":"EECS","discipline":"' + discipline + '","class_no":["'

			spl = st.split('/')
			course_id = None
			if len(spl) == 2:
				# output += str(spl[0]) +'","'+ str(spl[1])
				course_id = [spl[0], spl[1]]
			else:
				spl0 = spl[0]
				if ',' in spl0:
					res = re.split('[ ,]', spl0)
					if len(res[2]) >= 3:
						# output += str(res[0]) + '","' + str(res[2]) 
						course_id = [res[0], res[2]]
					else:
						# output += str(res[0]) + '-' + str(res[1]) + '","' + str(res[0]) + '-' + str(res[2])
						course_id = [str(res[0]) + '-' + str(res[1]), str(res[0]) + '-' + str(res[2])]
				else:
					# output += str(spl0)
					course_id = [str(spl0)]
				# print
			# output += '"],"course_title":"' 
			# print st
			paren_pos = trail.find('(')

			course_title = None
			if paren_pos > 0:
				# output += trail[:paren_pos].strip()
				course_title = trail[:paren_pos].strip()
			else:
				# output += trail.strip()
				course_title = trail.strip()

			return ManualCourseInfo('EECS', course_id, discipline, course_title)

					



def __main__():
	l = UndergraduateManualScraper()
	l.conv_ee()
	l.conv_ce()	
	l.conv_cs()
	for i in l.mapping:
		print i, l.mapping[i]


if __name__ == '__main__':
	__main__()