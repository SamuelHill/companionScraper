from __future__ import print_function	
import os.path
from lxml import html


ACM_INTEREST_FLAT_FILE_DIR = './inputs/ccs_flat.cfm.html'
ACM_INTEREST_HTML_TEXT = None
HIERARCHY = '//div[@id="holdflat"]'
GO_TO_LI = './li'
TOP_LEVEL_TEXT = './div/a/text()'
LOWER_LEVEL_TEXT = './ul/li/a/text()'

def get():
	if not os.path.isfile(ACM_INTEREST_FLAT_FILE_DIR):
		print('Cannot find file "./inputs/ccs_flat.cfm.html". Please manually download it from URL "http://dl.acm.org/ccs_flat.cfm"')
	cfm = open(ACM_INTEREST_FLAT_FILE_DIR, 'r')
	global ACM_INTEREST_HTML_TEXT
	ACM_INTEREST_HTML_TEXT = cfm.read()
	cfm.close()

def process(root, level):
	if root.tag == 'ul' or root.tag == 'div':
		for n in root:
			process(n, level)
	elif root.tag == 'li':
		for n in root:
			process(n, level+1)
	elif root.tag == 'a':
		 txt = root.xpath('./text()') 
		 if txt is not None and len(txt) > 0:
		 	for indent in range(0, level -1 ):
				print ('\t',end='')
		 	print (u'{0}'.format(txt[0]))


def __main__():
	get()
	process(html.fromstring(ACM_INTEREST_HTML_TEXT).xpath(HIERARCHY)[0], 0)


if __name__ == '__main__':
	__main__()