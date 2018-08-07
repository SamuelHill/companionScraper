import urllib
import os.path
from sets import Set

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from unidecode import unidecode 

import re

class InterestScraper:
	def __init__(self):
		if not os.path.isfile('./intermediate_results/eecs-undergraduate-manual.pdf'):
			urllib.urlretrieve('https://www.mccormick.northwestern.edu/eecs/documents/undergraduate/eecs-undergraduate-manual.pdf', './intermediate_results/eecs-undergraduate-manual.pdf')
		elif not os.path.isfile('./ug_manual_text.txt'):
			# self.text = re.sub(r'[^\x00-\x7F]+',' ', self.convert_pdf_to_txt('./intermediate_results/eecs-undergraduate-manual.pdf'))
			self.text = self.convert_pdf_to_txt('./intermediate_results/eecs-undergraduate-manual.pdf')
			manual = open('../intermediate_results/ug_manual_text.txt', 'w')
			manual.write(self.text)
			manual.close()
		else:
			manual = open('../intermediate_results/ug_manual_text.txt', 'r')
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
	def scrape_interests(self): 
		l = self.text.splitlines()
		lc = len(l)
		starts = False

		faculty_pattern = re.compile('^[A-Z][-a-zA-Z]+ ?([A-Z][.])? ?([A-Z][.])? ([A-Z]\\w+ )?[A-Z]\\w+(?=[,])')
		faculty_name = None
		faculty_interest = ''

		isIdentifyResearchInterest = False
		research_interest_pattern = re.compile('(?<=(^Research Interests: )).*')
		starts_interest_collection = False
		professor_pattern = re.compile('(Chair)|(Professor)|(Research Assistant)|(Research Associate)|(Research Faculty)|(Research Assistants)|(Emeritus Faculty)')

		final_interests = Set()
		for i in range(0, lc):
			li = l[i]
			if not starts:
				if li.startswith('Q&A sessions take place every Tuesday and Thursday afternoon. '):
					starts = True
			else:
				if li.startswith('The EECS Department has well-equipped instruction and research'):
					starts = False
			if starts:
				if li.startswith('EECS Undergraduate Study Manual'):
					li = li[43:]
				if li.startswith('Zahra Vashaei'):
					li = li[:13]+', '+li[13:]
				faculty_match = faculty_pattern.search(li)
				if faculty_match and self.isRejectingToken(li):
					if starts_interest_collection:
						if faculty_match and faculty_name is not None:
							interests = None
							if ';' in faculty_interest:
								interests = filter(None, re.split(';[ ]?', faculty_interest.strip()))
								print '{"faculty_name":"%s","fields":%s}' % (faculty_name, re.sub('\'', '"', str(interests)))
							else:
								interests = filter(None, re.split('[,][ ]?(?:and )?', faculty_interest.strip()))
								print '{"faculty_name":"%s","fields":%s}' % (faculty_name, re.sub('\'', '"', str(interests)))
							final_interests |= Set(interests)
							isIdentifyResearchInterest = False
							starts_interest_collection = False
							faculty_interest = ''
							faculty_name = None
					faculty_name = faculty_match.group(0)
					isIdentifyResearchInterest = True
				if isIdentifyResearchInterest:
					if not starts_interest_collection and li.startswith('Research Interests: '):
						starts_interest_collection = True
						faculty_interest += li[20:]
					elif starts_interest_collection:
						# if '' in li:
						# 	print li
						faculty_interest += li
		# interest_list = list(final_interests)
		# interest_list.sort()
		# for a in interest_list:
		# 	print a
	def isRejectingToken(self, string):
		if string.split(',')[0] in ['Sensor Networks', 'Nitride Semiconductors', 'Information Technology','New York']:
			return False
		return True



def __main__():
	s = InterestScraper()
	s.scrape_interests()


if __name__ == '__main__':
	__main__()