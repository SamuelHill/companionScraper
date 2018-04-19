# pip install lxml
# pip install requests
# pip install unidecode

from lxml import html
import requests
from unidecode import unidecode
from json_writer import *
import re

def getBaseURL(url):
	return re.search('.*/(?=[-a-zA-Z0-9]+[.]html)',url).group(0)

def stepInFacultyPage(index, name, url):
	# debug purpose
	# root_page_content = None
	# with open('./argall_faculty.html', u'r') as content_file:
	# 	root_page_content = content_file.read()
	# tree = html.fromstring(root_page_content)

	content = requests.get(url).content
	tree = html.fromstring(content)

	json = u'{ "doc_id":' + str(index).decode("utf-8") + u',"url":"' + url + u'","raw_content":"' 
	json += cleanHTML(content, True) 
	json += u'"' + getJSONElementFlat(u'name', name)

	# actual compute, faculty profile left
	profile_node = tree.xpath('//div[@id="faculty-profile-left"]')[0]
	json += getJSONElementFlat(u'address', u' '.join(profile_node.xpath('./text()')))

	phone = (profile_node.xpath('./a[@class="phone_link"]/@href'))
	if len(phone) > 0:
		json += getJSONElementFlat(u'phone_number', phone[0][6:])

	email = (profile_node.xpath('./a[@class="mail_link"]/@href'))
	if len(email) > 0:
		json += getJSONElementFlat(u'email', email[0][7:])

	webpages = profile_node.xpath('./p[following-sibling::h2 = "Departments" and preceding-sibling::h2[@class = "sites-header"] = "Website"]/a[@href]/@href')
	webpageNames = profile_node.xpath('./p[following-sibling::h2 = "Departments" and preceding-sibling::h2[@class = "sites-header"] = "Website"]/a[@href]/text()')
	json += getJSONListOfPairs('websites', webpageNames, webpages)
	personal_website_index = 0
	if len(webpageNames) > 0:
		for i in range(0, len(webpageNames)):
			if name in webpageNames[i]:
				personal_website_index = i
				break
		json += getJSONElementFlat(u'personal_website', webpages[personal_website_index])

	json += getJSONElementArray(u'departments', profile_node.xpath('./p[following-sibling::h2 = "Affiliations" and preceding-sibling::h2 = "Departments"]/a[@href]/text()'))
	json += getJSONElementArray(u'affiliations', profile_node.xpath('./p[preceding-sibling::h2 = "Affiliations"]/a[@href and not(text() = "Download CV")]/text()'))
	cv_link = profile_node.xpath('./p[preceding-sibling::h2 = "Affiliations"]/a[@href and text() = "Download CV"]/@href')
	if len(cv_link) > 0:
		json += getJSONElementFlat(u'cv_link', cv_link[0])

	# actual compute, faculty profile right
	profile_node = tree.xpath('//div[@id="faculty-profile-right"]')[0]
	json += getJSONElementArray(u'education', profile_node.xpath('./p[preceding-sibling::h2 = "Education" and following-sibling::h2 = "Research Interests"]/text()'))

	interests = u''.join(profile_node.xpath('./p[preceding-sibling::h2 = "Research Interests"]//text()'))

	json += getJSONElementFlat(u'interests', interests)

	# json += getJSONElementArray(u'publications', map(lambda x : unidecode(''.join(x.xpath('.//text()'))), profile_node.xpath('./ul[preceding-sibling::h2 = "Selected Publications"]/li')))

	json += u'}'
	return json
	


def main():
	res = stepInFacultyPage(1, u'Brenna Argall', u'http://www.mccormick.northwestern.edu/research-faculty/directory/profiles/argall-brenna.html')
	res += u'}'
	print res


if __name__ == "__main__":
	main()