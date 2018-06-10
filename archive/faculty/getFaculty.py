from lxml import html
import requests
import sys

VERBOSE = True if len(sys.argv) > 1 and sys.argv[1] == '1' else False

def printV(string):
	if VERBOSE and string is not None:
		print string

# IDENTIFIERS FOR NAVIGATING PAGES:
# PAGE_ALL_FAC = 'http://www.mccormick.northwestern.edu/eecs/people/faculty/'
# ALL_FACULTY = '//div[@class="faculty"]'
PAGE = 'http://www.mccormick.northwestern.edu/eecs/computer-science/people/'
FACULTY = '//div[@class="faculty cf"]'
FAC_SUBPAGES = './div[@class="faculty-info"]/h3/a[ @href]'
# DIVIDED CONTENT ON PAGE, one section for each sidebar/column
# Left side info:
LEFT_SIDEBAR = '//div[@id="faculty-profile-left"]'
PHONE_LINK = './a[@class="phone_link"]/@href'
MAIL_LINK = './a[@class="mail_link"]/@href'
WEBPAGES = ('./p[following-sibling::h2 = "Departments" and preceding-sibling::'
			'h2[@class = "sites-header"] = "Website"]/a[@href]/@href')
WEBPAGENAMES = ('./p[following-sibling::h2 = "Departments" and preceding-'
				'sibling::h2[@class = "sites-header"] = "Website"]/a[@href]'
				'/text()')  # sloppy multiline strings...
DEPARTMENTS = ('./p[following-sibling::h2 = "Affiliations" and preceding-'
			   'sibling::h2 = "Departments"]/a[@href]/text()')
AFFILIATIONS = ('./p[preceding-sibling::h2 = "Affiliations"]/a[@href and'
				' not(text() = "Download CV")]/text()')
CV_HREF = ('./p[preceding-sibling::h2 = "Affiliations"]/a[@href and text() ='
		   ' "Download CV"]/@href')
# Right side info:
RIGHT_SIDEBAR = '//div[@id="faculty-profile-right"]'
EDUCATION = ('./p[preceding-sibling::h2 = "Education" and following-sibling::'
			 'h2 = "Research Interests"]/text()')
INTERESTS = './p[preceding-sibling::h2 = "Research Interests"]//text()'
# GENERAL TAGS
TEXT = './text()'
HREF = './@href'
HTTP = 'http:'

htmlContent = requests.get(PAGE).content
tree = html.fromstring(htmlContent)
facultyNodes = tree.xpath(FACULTY)
for facultyNode in facultyNodes:
	# Gathering faculty page...
	node = facultyNode.xpath(FAC_SUBPAGES)[0]
	# NAME
	name = node.xpath(TEXT)[0]
	printV(name)
	# ENTITY ID - need to be able to resolve on multiple iterations
	newName = name.replace(" ", "")
	# Continue getting url and content...
	url = HTTP + node.xpath(HREF)[0]
	content = requests.get(url).content
	tree = html.fromstring(content)
	# Begin going through sidebar information for each faculty, left sidebar...
	sidebar = tree.xpath(LEFT_SIDEBAR)[0]
	# ADDRESS (room number)
	address = sidebar.xpath(TEXT)
	roomNumber = address[1] if len(address) > 1 else None
	printV(roomNumber)
	# PHONE NUMBER
	phone = sidebar.xpath(PHONE_LINK)
	phone_number = phone[0][6:] if len(phone) > 0 else None
	printV(phone_number)
	# EMAIL
	mail = sidebar.xpath(MAIL_LINK)
	email = mail[0][7:] if len(mail) > 0 else None
	printV(email)
	# WEBSITES (distinguishing personal site too)
	webpages = sidebar.xpath(WEBPAGES)
	webpageNames = sidebar.xpath(WEBPAGENAMES)
	websites = zip(webpages, webpageNames)
	personal_website = None
	if len(websites) > 0:
		for page, pageName in websites:
			if name in pageName:
				personal_website = page
				break
	printV(personal_website)
	for page, pageName in websites:
		printV(pageName + ": \n\t" + page)
	# DEPARTMENTS
	department_list = sidebar.xpath(DEPARTMENTS)
	departments = department_list if len(department_list) > 0 else None
	printV(departments)
	# AFFILIATIONS
	affiliations_list = sidebar.xpath(AFFILIATIONS)
	affiliations = affiliations_list if len(affiliations_list) > 0 else None
	printV(affiliations)
	# CV
	cv_link = sidebar.xpath(CV_HREF)
	cv = cv_link[0] if len(cv_link) > 0 else None
	printV(cv)
	# Begin going through remaining sidebar information, right side...
	sidebar = tree.xpath(RIGHT_SIDEBAR)[0]
	# EDUCATION
	education_list = sidebar.xpath(EDUCATION)
	education = education_list if len(education_list) > 0 else None
	printV(education)
	# INTERESTS
	interests_list = sidebar.xpath(INTERESTS)
	interests = interests_list if len(interests_list) > 0 else None
	printV(interests)

	# Basic meld stuff...
	print "(SocialModelFn " + newName + ")"
	print "(isa " + newName + " NUPerson)"
	print "(isa " + newName + " NUFaculty)"
	print "(in-microtheory PeopleDataMt)"
	if education is not None:
		for edu in education:
			if "Ph.D" in edu:
				print "(isa " + newName + " AcademicProfessional)"
				print "(titleOfPerson " + newName + " Dr)"
				break
		# for edu in education:
		# 	if "Ph.D" in edu:
		# 		print "(schooling Hinrichs CornellUniversity Graduate)"
	if phone_number:
		print "(phoneNumberOf " + newName +  " \"" + phone_number + "\")"
	print "(emailOf " + newName +  " \"" + email + "\")"
	if personal_website:
		print "(personalWebsite " + newName +  " \"" + personal_website + "\")"
	print "(officeLocation " + newName +  " \"" + " ".join(address) + "\")"
	# SECOND MT BEING USED - PLAIN ENGLISH NAMING
	print "(in-microtheory EnglishMt)"
	print "(fullName " + newName + " \"" + name + "\")"
	print