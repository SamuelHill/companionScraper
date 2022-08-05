#!/usr/bin/python
# -*- coding: utf-8 -*-
# 3.6
from datetime import datetime, timedelta, date
from selenium import webdriver  # pip3 install selenium
# download a browser driver, I use chromedriver in this for now.
# mv /Users/samuelhill/Downloads/chromedriver /usr/local/bin/chromedriver
# on mac:
#       brew install chromedriver
#       brew tap homebrew/cask
#       brew cask install chromedriver
from lxml import html  # pip3 install lxml
import requests  # pip3 install requests
import regex as re  # pip3 install regex
import string
import os
import time

##############################################################################
#                              HELPER FUNCTIONS                              #
##############################################################################


def real_dirname():
    return os.path.dirname(os.path.realpath(__file__))


def xpathToList(source, xpath_text):
    xpath_list = source.xpath(xpath_text)
    return xpath_list if len(xpath_list) > 0 else None


def xpathToCleanString(source, xpath_text):
    xpath_list = xpathToList(source, xpath_text)
    if xpath_list:
        utf8_safe = str(' '.join(xpath_list))
        return utf8_safe.translate(str.maketrans('','','\t\n')).strip()
    else:
        return None


def xpathToExistsBool(source, xpath_text):
    return False if xpathToList(source, xpath_text) is None else True


def uniqueID(name):
    printable = set(string.printable)
    filtered_name = ''.join([x for x in name if x in printable])
    no_punc = filtered_name.translate(str.maketrans('','',string.punctuation))
    return no_punc.replace(' ', '')


def lispStyle(pred, args):
    return '(' + pred + ' ' + ' '.join(args) + ')'


def isa(arg1, arg2):
    return lispStyle('isa', [arg1, arg2])


def toFile(meld, filename):
    f = open(real_dirname() + '/' + filename + '.meld', 'w+')
    f.write(meld)
    f.close()

##############################################################################
#                           COLLEGE MELD FUNCTIONS                           #
##############################################################################


def scrapeColleges():
    # list of all colleges and universities from some website...
    PARTIAL  = 'https://www.4icu.org/reviews/index'
    all_colleges = []
    for page in [PARTIAL + str(i) + '.htm' for i in range(28)]:
        tree = html.fromstring(requests.get(page).content)
        for college in tree.xpath('//tbody/tr/td/a[@href]/text()'):
            all_colleges.append(college)
    return all_colleges


def meldColleges(colleges):
    meld = '(in-microtheory CollegeNamesMt)\n'
    for college in colleges:
        if college:
            college = str(college).strip()
            college_id = uniqueID(college)
            meld += isa(college_id, 'College') + '\n'
            args = [college_id, '"' + college + '"']
            meld += lispStyle('prettyString', args) + '\n\n'
    return meld.strip()

##############################################################################
#                           FACULTY MELD FUNCTIONS                           #
##############################################################################


def scrapeFacultyData():
    # IDENTIFIERS FOR NAVIGATING FACULTY PAGE:
    BASE_PAGE = 'http://www.mccormick.northwestern.edu'
    EECS_PEOPLE = '/eecs/computer-science/people/'
    FACULTY_PAGE = BASE_PAGE + EECS_PEOPLE
    # list of faculty pages, href to each faculty details page
    FACULTY_PAGES = '//div[@class="faculty-info"]/h3/a[@href]/@href'
    # attributes to look for on faculty details page
    FACULTY_NAME = '//h1[@id="page-title"]/text()'
    ADDRESS      = '//div[@id="faculty-profile-left"]/text()'
    PHONE_LINK   = '//a[@class="phone_link"]/@href'
    MAIL_LINK    = '//a[@class="mail_link"]/@href'
    WEBPAGES     = ('//p[following-sibling::h2 = "Departments" and preceding-'
                    'sibling::h2[@class = "sites-header"] = "Website"]'
                    '/a[@href]/@href')
    WEBPAGENAMES = ('//p[following-sibling::h2 = "Departments" and preceding-'
                    'sibling::h2[@class = "sites-header"] = "Website"]/'
                    'a[@href]/text()')
    DEPARTMENTS  = ('//p[following-sibling::h2 = "Affiliations" and preceding'
                    '-sibling::h2 = "Departments"]/a[@href]/text()')
    AFFILIATIONS = ('//p[preceding-sibling::h2 = "Affiliations"]/a[@href and '
                    'not(text() = "Download CV")]/text()')
    CV_HREF      = ('//p[preceding-sibling::h2 = "Affiliations"]/a[@href and '
                    'text() = "Download CV"]/@href')
    EDUCATION    = ('//p[preceding-sibling::h2 = "Education" and following-'
                    'sibling::h2 = "Research Interests"]/text()')
    INTERESTS    = '//p[preceding-sibling::h2 = "Research Interests"]//text()'
    # SCRAPE:
    # get base cs faculty listing website
    base_content = requests.get(FACULTY_PAGE).content
    base_tree = html.fromstring(base_content)
    # grab faculty from page as list,
    faculty_pages = base_tree.xpath(FACULTY_PAGES)
    # loop over every faculty on this page and collect scraped faculty data
    all_faculty = []
    for faculty_page in faculty_pages:
        # setup faculty data for each faculty
        faculty = dict.fromkeys(['name', 'ID', 'address', 'cv_link',
                                 'phone_number', 'personal_site', 'email',
                                 'departments', 'affiliations', 'websites',
                                 'education', 'interests'], None)
        # go to specific faculty detail page, check that page is one of ours
        # (3 pages are not and have hull https:// links...)
        if not faculty_page.startswith('http'):
            faculty_page = 'http:' + faculty_page
        else:
            continue  # don't have parsers for personal/outside sites.
        content = requests.get(faculty_page).content
        tree = html.fromstring(content)
        # scrape faculty data
        faculty['name']          = xpathToCleanString(tree, FACULTY_NAME)
        faculty['ID']            = uniqueID(faculty['name'])
        faculty['address']       = xpathAddress(tree, ADDRESS)
        faculty['room_number']   = xpathRoomNumber(tree, ADDRESS)
        faculty['phone_number']  = xpathPhoneNumber(tree, PHONE_LINK)
        faculty['email']         = xpathEmail(tree, MAIL_LINK)
        faculty['websites']      = xpathZipLists(tree, WEBPAGES, WEBPAGENAMES)
        faculty['personal_site'] = personalSite(faculty)
        faculty['departments']   = xpathToList(tree, DEPARTMENTS)
        faculty['affiliations']  = xpathToList(tree, AFFILIATIONS)
        faculty['cv_link']       = xpathToCleanString(tree, CV_HREF)
        faculty['education']     = xpathToList(tree, EDUCATION)
        faculty['interests']     = xpathToCleanString(tree, INTERESTS)
        # collect all faculty data
        all_faculty.append(faculty)
    return all_faculty


def getFacultyOntologized(faculty, colleges):
    args = '(SocialModelMtFn ' + faculty['ID'] + ')'
    meld = lispStyle('in-microtheory', [args]) + '\n'
    meld += isa(faculty['ID'], 'NUPerson') + '\n'
    meld += isa(faculty['ID'], 'NUFaculty') + '\n'
    meld += lispStyle('department', [faculty['ID'], 'ComputerScience']) + '\n'
    if faculty['departments']:
        for department in faculty['departments']:
            if department != 'Electrical Engineering and Computer Science':
                args = [faculty['ID'], uniqueID(department)]
                meld += lispStyle('department', args) + '\n'
    if faculty['education'] is not None:
        # degreeInField
        for edu in faculty['education']:
            if 'Ph.D' in edu:
                meld += isa(faculty['ID'], 'AcademicProfessional') + '\n'
                args = [faculty['ID'], 'Dr']
                meld += lispStyle('titleOfPerson', args) + '\n'
                break
        for edu in faculty['education']:
            all_degrees = [{'degree':'Ph.D',    'normal':'PhD'},
                           {'degree':'M.S',     'normal':'MS'},
                           {'degree':'MS',      'normal':'MS'},
                           {'degree':'M.A',     'normal':'MA'},
                           {'degree':'B.S',     'normal':'BS'},
                           {'degree':'BS',      'normal':'BS'},
                           {'degree':'B.A',     'normal':'BA'},
                           {'degree':'B.E',     'normal':'BE'},
                           {'degree':'M.E',     'normal':'ME'},
                           {'degree':'M. Mus',  'normal':'MM'},
                           {'degree':'B. Mus',  'normal':'BM'},
                           {'degree':'Master of Fine Arts', 'normal':'MFA'},
                           {'degree':'B. Tech', 'normal':'BT'},
                           {'degree':'A.B',     'normal':'AB'},
                           {'degree':'S.M',     'normal':'SM'},
                           {'degree':'S.B',     'normal':'SB'},
                           {'degree':'B.CSci',  'normal':'BCS'}]
            for degree in all_degrees:
                if degree['degree'] in edu:
                    ID = faculty['ID']
                    meld += schooling(edu, degree['normal'], colleges, ID)
                    break
    if faculty['phone_number']:
        phone = faculty['phone_number']
        meld += lispStyle('phoneNumberOf', [faculty['ID'], '"' + phone + '"'])
        meld += '\n'
    args = [faculty['ID'], '"' + faculty['email'] + '"']
    meld += lispStyle('emailOf', args) + '\n'
    if faculty['personal_site']:
        args = [faculty['ID'], '"' + faculty['personal_site'] + '"']
        meld += lispStyle('personalWebsite', args) + '\n'
    args = [faculty['ID'], '"' + faculty['room_number'] + '"']
    meld += lispStyle('officeLocation', args) + '\n'
    meld += lispStyle('in-microtheory', ['EnglishMt']) + '\n'
    meld += lispStyle('fullName', [faculty['ID'], '"' + faculty['name'] + '"'])
    splitName = faculty['name'].split(' ')
    lastName = splitName[-1:][0]
    args = ['(TheList professor)', lastName, faculty['ID']]
    meld += '\n' + lispStyle('indexedProperName', args) + '\n'
    args = ['(TheList ' + splitName[0] + ')', lastName, faculty['ID']]
    meld += lispStyle('indexedProperName', args) + '\n'
    args = ['(TheList doctor)', lastName, faculty['ID']]
    meld += lispStyle('indexedProperName', args) + '\n'
    return meld + '\n'


def xpathZipLists(source, xpath_text_1, xpath_text_2):
    xpath_list_1 = xpathToList(source, xpath_text_1)
    xpath_list_2 = xpathToList(source, xpath_text_2)
    if xpath_list_1 and xpath_list_2:
        return list(zip(xpath_list_1, xpath_list_2))
    return []


def xpathAddress(source, xpath_text):
    xpath_list = xpathToList(source, xpath_text)
    spacing = xpath_list[0] + ' ' + xpath_list[2]
    return spacing if len(xpath_list) > 0 else None


def xpathRoomNumber(source, xpath_text):
    xpath_list = xpathToList(source, xpath_text)
    if len(xpath_list) > 1:
        return xpath_list[1]
    return None


def xpathPhoneNumber(source, xpath_text):
    phone_number = xpathToCleanString(source, xpath_text)
    if phone_number:
        return phone_number[6:]  # remove the phone number link tel://
    return None


def xpathEmail(source, xpath_text):
    email = xpathToCleanString(source, xpath_text)
    if email:
        return email[7:]  # remove the email link mailto:
    return None


def personalSite(faculty_data):
    if len(faculty_data['websites']) > 0:
        for page, pageName in faculty_data['websites']:
            if faculty_data['name'] in pageName:
                return page
    return None


def schooling(edu, degree, colleges, facultyID):
    meld = ''
    splitedu = edu.split(',')
    found = False
    options = []
    for college in colleges:
        if college in edu:
            args = [facultyID, uniqueID(college), degree]
            meld += lispStyle('schooling', args) + '\n'
            found = True
            break  # Exact match, look no further
        if len(splitedu) > 1:
            if splitedu[1] in college:
                options.append(college)
    if not found:
        if len(options) > 0:
            collegeID = uniqueID(options[0])
            args = [facultyID, collegeID, degree]
            meld += lispStyle('schooling', args) + '\n'
        elif len(options) > 1:
            for option in options:
                if splitedu[2] in option:
                    collegeID = uniqueID(option)
                    args = [facultyID, collegeID, degree]
                    meld += lispStyle('schooling', args) + '\n'
                    break
        extras = [{'text':'MIT',
                   'id':'MassachusettsInstituteofTechnology'},
                  {'text':'M.I.T.',
                   'id':'MassachusettsInstituteofTechnology'},
                  {'text':'UCLA',
                   'id':'UniversityofCaliforniaLosAngeles'},
                  {'text':'State University of New York, Stony Brook',
                   'id':'StonyBrookUniversity'},  # SUNY schools are confusing
                  {'text':'University of Illinois at Urbana',
                   'id':'UniversityofIllinoisatUrbanaChampaign'},
                  {'text':'UC Santa Barbara',
                   'id':'UniversityofCaliforniaSantaBarbara'},
                  {'text':'Aristotelian University of Thessaloniki',
                   'id':'AristotleUniversityofThessaloniki'},
                  {'text':'Bogazici Univeristy',
                   'id':'BogaziciUniveristy'},  # BogaziçiÜniversitesi
                  {'text':'Tel-Aviv University',
                   'id':'TelAvivUniversity'},
                  {'text':'University of Belgrade',
                   'id':'UniversityofBelgrade'},  # not listed at all...
                  {'text':'Brown Univesity',
                   'id':'BrownUniversity'},
                  {'text':'University of Sts. Kiril and Metodij',
                   'id':'SaintsCyrilandMethodiusUniversityofSkopje'},  # not listed at all...
                  {'text':'Indian Institute of Technology, Madras',
                   'id':'IndianInstituteofTechnologyMadras'},
                  {'text':'I am an Associate Professor at the EECS',
                   'id':'Princeton University'}]
        for extra in extras:
            if extra['text'] in edu:
                args = [facultyID, extra['id'], degree]
                meld += lispStyle('schooling', args) + '\n'
                break
    return meld


def facultyMeld(colleges):
    meld = ''
    for faculty in scrapeFacultyData():
        meld += getFacultyOntologized(faculty, colleges)
    return meld.strip()

##############################################################################
#                            EVENT MELD FUNCTIONS                            #
##############################################################################


def scrapeEventData():
    # IDENTIFIERS FOR NAVIGATING EVENT PAGE:
    EVENTS_PAGE = 'https://planitpurple.northwestern.edu'
    # list of events, can get href to event detail page
    EVENTS_LIST = '//ul[@class="events"]/li/a/@href'
    # attributes to look for on event details page
    EVENT_NAME    = '//div[@class="event_header"]/h2/text()'
    REOCCURRING   = '//p[@id="recurring"]'
    AUDIENCE_TEXT = '//span[text()[contains(.,"Audience")]]/../text()'
    CATEGORY_TEXT = '//span[contains(@class, "event_category")]/text()'
    CONTACT_TEXT  = '//span[text()[contains(.,"Contact")]]/../text()'
    CONTACT_MAIL  = '//span[text()[contains(.,"Contact")]]/../a/text()'
    WHERE_TEXT    = '//span[text()[contains(.,"Where")]]/../text()'
    GROUP_TEXT    = '//span[text()[contains(.,"Group")]]/../a/text()'
    WHEN_TEXT     = '//span[text()[contains(.,"When")]]/../text()'
    COST_TEXT     = '//span[text()[contains(.,"Cost")]]/../text()'
    # SCRAPE:
    today = date.today()
    oneweek = timedelta(days = 7)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    all_events = []
    for x in range(4):  # 8 weeks ~= 2 months
        today_search = '/#search=' + str(today) + '/0/1+5/1//week'
        # get base event listing website
        driver.get(EVENTS_PAGE + today_search)
        time.sleep(1)
        htmlContent = driver.page_source
        # htmlContent = requests.get(url).content
        mainTree = html.fromstring(htmlContent)
        # grab events from page as list,
        event_pages = mainTree.xpath(EVENTS_LIST)
        # loop over every event on this page and collect scraped event data
        used_events = []
        for event_page in event_pages:
            # setup event data for each event
            event = dict.fromkeys(['url', 'event_name', 'month', 'day', 'time',
                                   'day_of_week', 'reoccurring', 'location',
                                   'audience', 'contact', 'group', 'cost',
                                   'date_time', 'ID', 'category'], None)
            event['url'] = EVENTS_PAGE + event_page
            # go to specific event detail page
            driver.get(event['url'])
            content = driver.page_source
            # content = requests.get(EVENTS_PAGE + event_page).content
            tree = html.fromstring(content)
            # scrape event data
            name = xpathToCleanString(tree, EVENT_NAME)
            clean_name = name.replace('“', '\\"').replace('"', '\\"')
            if name not in used_events:
                event['event_name'] = clean_name
                event['ID']         = uniqueID(event['event_name'])
                used_events.append(event['event_name'])
                event['reoccurring'] = xpathToExistsBool(tree, REOCCURRING)
                event['date_time']   = xpathToCleanString(tree, WHEN_TEXT)
                event['location']    = xpathToCleanString(tree, WHERE_TEXT)
                event['audience']    = xpathToCleanString(tree, AUDIENCE_TEXT)
                event['contact']     = xpathToCleanString(tree, CONTACT_TEXT)
                event['contact_mail']= xpathToCleanString(tree, CONTACT_MAIL)
                event['group']       = xpathToCleanString(tree, GROUP_TEXT)
                event['cost']        = xpathToCleanString(tree, COST_TEXT)
                event['category']    = xpathToCleanString(tree, CATEGORY_TEXT)
                # collect all event data
                all_events.append(event)
        today += oneweek
    driver.close()
    return all_events


def getEventOnotologized(event):
    times, year, month, day = dayMonthYear(event['date_time'])
    new_id = 'NUEvent-' + str(year) + '-' + str(month)[:3] + '-' + str(day)
    new_id += '-' + uniqueID(event['event_name'])[:30]
    meld = lispStyle('in-microtheory', ['(NUEventMtFn', new_id + ')'])
    meld += '\n' + isa(new_id, 'NUEvent') + '\n'
    date, duration = dateAndDuration(times, year, month, day)
    meld += lispStyle('dateOfEvent', [new_id, date]) + '\n'
    meld += lispStyle('durationOfEvent', [new_id, duration]) + '\n'
    temp_args = [new_id, '"' + event['event_name'] + '"']
    meld += lispStyle('eventName', temp_args) + '\n'
    if event['location']:
        temp_args = [new_id, '"' + event['location'] + '"']
        meld += lispStyle('eventLocale', temp_args) + '\n'
    temp_args = [new_id, '"' + event['group'] + '"']
    meld += lispStyle('eventHost', temp_args) + '\n'
    ################
    # NOT YET USED #
    ################
    con_name, con_phone = processEventContact(event['contact'])
    if con_name:
        temp_args = [new_id, '"' + con_name + '"']
        meld += lispStyle('eventHostContact', temp_args) + '\n'
    if con_phone:
        temp_args = [new_id, '"' + con_phone + '"']
        meld += lispStyle('eventHostContact', temp_args) + '\n'
    if event['contact_mail']:
        temp_args = [new_id, '"' + event['contact_mail'] + '"']
        meld += lispStyle('eventHostContact', temp_args) + '\n'
    ################
    audiences = event['audience'].split(' - ')
    temp_args = [new_id, 'NUPerson']
    meld += lispStyle('eventAudience', temp_args) + '\n'
    for audience in audiences:
        if audience == 'Faculty/Staff':
            temp_args = [new_id, 'NUFaculty']
            meld += lispStyle('eventAudience', temp_args) + '\n'
            temp_args = [new_id, 'NUStaff']
            meld += lispStyle('eventAudience', temp_args) + '\n'
        elif audience == 'Post Docs/Docs':
            temp_args = [new_id, 'NUPhDStudent']
            meld += lispStyle('eventAudience', temp_args) + '\n'
            temp_args = [new_id, 'NUMastersStudent']
            meld += lispStyle('eventAudience', temp_args) + '\n'
        elif audience == 'Student':
            temp_args = [new_id, 'NUStudent']
            meld += lispStyle('eventAudience', temp_args) + '\n'
            temp_args = [new_id, 'NUUndergraduate']
            meld += lispStyle('eventAudience', temp_args) + '\n'
        elif audience == 'Public':
            temp_args = [new_id, 'NUVisitor']
            meld += lispStyle('eventAudience', temp_args) + '\n'
        elif audience == 'Graduate Students':
            temp_args = [new_id, 'NUGraduateStudent']
            meld += lispStyle('eventAudience', temp_args) + '\n'
    ################
    if event['reoccurring']:
        temp_args = [new_id, 't']
        meld += lispStyle('eventReoccurring', temp_args) + '\n'
    ################
    if event['cost']:
        temp_args = [new_id, '"' + event['cost'] + '"']
        meld += lispStyle('eventCost', temp_args) + '\n'
    ################
    if event['category']:
        temp_args = [new_id, '"' + event['category'] + '"']
        meld += lispStyle('eventCategory', temp_args) + '\n'
    return meld + '\n'


def dayMonthYear(date_time):
    date = date_time.split(',')
    times = date[2].split()
    year = times[0]
    month, day = date[1].replace(',', '').split()
    return times, year, month, day


def dateAndDuration(times, year, month, day):
    date_text = '(YearFn ' + str(year) + ')'
    date_text = '(MonthFn ' + month + ' ' + date_text + ')'
    date_text = '(DayFn ' + day + ' ' + date_text + ')'
    times[1] = times[1].strip().replace('\\t', '').replace('\\n', '')
    if times[1] == 'All':
        duration = '(DaysDuration 1)'
    else:
        start_hr, start_min = splitHourMinute(times[1], times[2])
        date_text = '(HourFn ' + start_hr + ' ' + date_text + ')'
        date_text = '(MinuteFn ' + start_min + ' ' + date_text + ')'
        end_hr, end_min = splitHourMinute(times[4], times[5])
        start = start_hr + ':' + start_min
        end = end_hr + ':' + end_min
        duration = '(MinutesDuration ' + str(calcDuration(start, end)) + ')'
    return date_text, duration


def splitHourMinute(time, day_half):
    hours, minutes = time.split(':')
    if day_half == 'PM':
        hours = str(int(hours) + 12) if int(hours) != 12 else '12'
    else:
        hours = str(hours) if int(hours) != 12 else '0'
    return hours, minutes


def calcDuration(start_time, end_time):
    FMT = '%H:%M'
    start = datetime.strptime(start_time, FMT)
    end = datetime.strptime(end_time, FMT)
    duration = end - start
    return duration.seconds//60


def processEventContact(contact):
    printable = set(string.printable)
    filtered_contact = ''.join([x for x in contact if x in printable])
    phone_regex = re.compile('\d{3}.\d{3}.\d{4}')
    phone_match = phone_regex.findall(filtered_contact)
    if phone_match:
        name = filtered_contact.replace(phone_match[0], '').strip()
        return name, phone_match[0]
    return filtered_contact.strip(), None


def eventMeld():
    meld = ''
    for event in scrapeEventData():
        meld += getEventOnotologized(event)
    return meld.strip()

##############################################################################
#                             END FUNCTION DEFS                              #
##############################################################################


def main():
    ########
    print('colleges')
    colleges = scrapeColleges()
    collegesMeld = meldColleges(colleges)
    # print collegesMeld
    toFile(collegesMeld, 'colleges')
    ########
    print('faculty')
    faculty = facultyMeld(colleges)
    # print faculty
    toFile(faculty, 'faculty')
    ########
    print('events')
    events = eventMeld()
    # print events
    toFile(events, 'events')


if __name__ == '__main__':
    main()
