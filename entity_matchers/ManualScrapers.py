import urllib
import os.path

# need to install PDFMiner from https://github.com/euske/pdfminer/, which supports python 2.x

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from unidecode import unidecode 

import re

class UndergraduateManualScraper:
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
				    print found
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
					print found
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
					print found


def __main__():
	l = UndergraduateManualScraper().conv_ee()



if __name__ == '__main__':
	__main__()