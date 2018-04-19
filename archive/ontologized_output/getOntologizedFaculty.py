# Requires Python 2.x
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# pip install lxml
# pip install requests

from lxml import html
import requests

verbose = False

def printV(string):
	if verbose:
		print string

def cleanHTML(content, isDecode = False):
	if isDecode is True:
		cleaned_content = content.decode('utf-8')
	else:
		cleaned_content = content
	if '\t' in cleaned_content:
		cleaned_content=cleaned_content.replace('\t','\\t')
	if '\r' in cleaned_content:
		cleaned_content=cleaned_content.replace('\r','\\r')
	if '\n' in cleaned_content:
		cleaned_content=cleaned_content.replace('\n','\\n')
	for ch in ['"', '\xe2\x80\x9d'.decode('utf8'), '\xe2\x80\x9c'.decode('utf8')]:
		if ch in cleaned_content:
			cleaned_content=cleaned_content.replace(ch,'\\' + ch)
	if '\\\\"' in cleaned_content:
		cleaned_content=cleaned_content.replace('\\\\"','\\\\\\"')
	return cleaned_content

page = requests.get('http://www.mccormick.northwestern.edu/eecs/people/faculty/')
tree = html.fromstring(page.content)
faculty = tree.xpath('//div[@class="faculty"]')
for fac in faculty:
	# Gathering faculty pages (nodes)
	node = fac.xpath('./div[@class="faculty-info"]/h3/a[ @href]')[0]
	url = 'http:' + node.xpath('./@href')[0]
	content = requests.get(url).content
	tree = html.fromstring(content)

	# Getting the name (both for later lookup and for naming things)
	name = node.xpath('./text()')[0]
	printV(str(name))

	newName = name
	newName = newName.replace(" ", "")
	print "(in-microtheory EnglishMt)"
	print "(fullName " + newName + " \"" + name + "\")"
	print "(in-microtheory CyclistDefinitionalMt)"
	print "(isa " + newName + " HumanCyclist)"
	print "(in-microtheory PeopleDataMt)"

	# Begin going through profile information...
	profile = tree.xpath('//div[@id="faculty-profile-left"]')[0]

	# ADDRESS
	address = cleanHTML(profile.xpath('./text()'))
	printV("\t" + str(address))

	# PHONE NUMBER
	phone = (profile.xpath('./a[@class="phone_link"]/@href'))
	if len(phone) > 0:  # filter out blanks
		phone_number = cleanHTML(phone[0][6:])
		printV("\t" + str(phone_number))

	# EMAIL
	mail_link = (profile.xpath('./a[@class="mail_link"]/@href'))
	if len(mail_link) > 0:  # filter out blanks
		email = cleanHTML(mail_link[0][7:])
		printV("\t" + str(email))

	# WEBPAGES
	webpages = profile.xpath('./p[following-sibling::h2 = "Departments" and preceding-sibling::h2[@class = "sites-header"] = "Website"]/a[@href]/@href')
	webpageNames = profile.xpath('./p[following-sibling::h2 = "Departments" and preceding-sibling::h2[@class = "sites-header"] = "Website"]/a[@href]/text()')
	# json += getJSONListOfPairs('websites', webpageNames, webpages)
	websites = zip(webpageNames, webpages)
	printV("\t" + str(websites))

	# PERSONAL WEBSITE (distinction)
	personal_website_index = 0
	if len(webpageNames) > 0:
		for i in range(0, len(webpageNames)):
			if name in webpageNames[i]:
				personal_website_index = i
				break
		personal_website = webpages[personal_website_index]
		printV("\t" + str(personal_website))

	# DEPARTMENTS
	departments = profile.xpath('./p[following-sibling::h2 = "Affiliations" and preceding-sibling::h2 = "Departments"]/a[@href]/text()')
	printV("\t" + str(departments))

	# AFFILIATIONS
	affiliations = profile.xpath('./p[preceding-sibling::h2 = "Affiliations"]/a[@href and not(text() = "Download CV")]/text()')
	printV("\t" + str(affiliations))

	# CV
	cv_link = profile.xpath('./p[preceding-sibling::h2 = "Affiliations"]/a[@href and text() = "Download CV"]/@href')
	if len(cv_link) > 0:
		cv = cv_link[0]
		printV("\t" + str(cv))

	# Begin going through remaining profile information...
	profile = tree.xpath('//div[@id="faculty-profile-right"]')[0]

	# EDUCATION
	education = profile.xpath('./p[preceding-sibling::h2 = "Education" and following-sibling::h2 = "Research Interests"]/text()')
	printV("\t" + str(education))

	for edu in education:
		if "Ph.D" in edu:
			print "(isa " + newName + " AcademicProfessional)"
			# (hasDegreeInField Hinrichs PhDDegree ComputerScience)
			# (schooling Hinrichs CornellUniversity Graduate)
			# (schooling Hinrichs GeorgiaInstituteOfTechnology-University Graduate)
			print "(titleOfPerson " + newName + " Dr)"
			break

	# INTERESTS
	interests = profile.xpath('./p[preceding-sibling::h2 = "Research Interests"]//text()')
	printV("\t" + str(interests))
	print
	print