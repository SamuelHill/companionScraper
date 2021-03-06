import re
import json
import codecs
import os.path
import ahocorasick
import api_python3_interests_and_related as iar

data_directory='data/'

#################################################
### Utility Functions

'''
Load a keyword file and create an Aho-Corasick keyword matching automation.
The keywords are expected to be in the same line and are separated by tabs.
Returns the newly created automation
'''
def createSingleAutomation(file_name):
	A = ahocorasick.Automaton()

	list_txt = open(data_directory + file_name, 'r')
	list_split = list_txt.read().lower().split('\t')
	list_txt.close()

	for idx, key in enumerate(list_split):
		A.add_word(key, (idx, key))

	A.make_automaton()
	return A

'''
Return a list of distinct keyword matches
'''
def matchKeywordsWithAutomation(A, string):
	output = set()
	for end_index, (insert_order, original_value) in A.iter(string):
		start_index = end_index - len(original_value) + 1
		assert string[start_index:start_index + len(original_value)] == original_value
		output.add(original_value)
	return list(output)

'''
Take a keyword taxonomy file and turn it into the appropriate tab-separated inputs required by function 'createSingleAutomation'. 
The levels of specialization for the keywords are denoted by the number of tabs precede the keyword. 
Short terms like 'ai' are preceded with a single space character, i.e. ' ai'
See README for more detail
'''
def reconstructConceptList(input_file_name):
	output = ''
	with codecs.open(data_directory+input_file_name, mode='r', encoding='utf-8') as f:
		for line in f:
			output += line
	output = re.sub(r'[\t\r\n]+', '\t', output).lower()
	with open(data_directory+'list_form_'+input_file_name, 'w') as o:
		o.write(output)

'''
Construct all automations needed for matching interests and return a dictionary that contain each one, marked by the category of the automation. 
'''
def createAutomationsForInterests(is_reconstructing):
	if is_reconstructing or not os.path.isfile(data_directory+'list_form_concept_hierarchy_cs.txt'):
		reconstructConceptList('concept_hierarchy_cs.txt')
		reconstructConceptList('concept_hierarchy_ce.txt')
		reconstructConceptList('concept_hierarchy_ee.txt')
		reconstructConceptList('concept_hierarchy_math.txt')
		if os.path.isfile(data_directory+'concept_list_additional.txt'):
			reconstructConceptList('concept_hierarchy_additional.txt')
	output = {}
	output['CS'] = createSingleAutomation('list_form_concept_hierarchy_cs.txt')
	output['CE'] = createSingleAutomation('list_form_concept_hierarchy_ce.txt')
	output['EE'] = createSingleAutomation('list_form_concept_hierarchy_ee.txt')
	output['Math'] = createSingleAutomation('list_form_concept_hierarchy_math.txt')
	if os.path.isfile(data_directory+'list_form_concept_hierarchy_additional.txt'):
		output['EECS_additional'] = createSingleAutomation('list_form_concept_hierarchy_additional.txt')
	return output

'''
Resolve abbreviations. Will turn ' ai' into 'artificial intelligence'
'''
def toFullTerms(domain, text):
	if domain not in abbreviationResolver:
		return text
	if text not in abbreviationResolver[domain]:
		return text
	return abbreviationResolver[domain][text]

'''
Load curated list of interests for EECS faculties, match their interests entries for keywords, and return the result faculty-interests dictionary
'''
def getCuratedFacultyInterestList(automations, name_of_the_jl_file):
	output = {}
	with codecs.open(data_directory+name_of_the_jl_file, mode='r', encoding='utf-8') as f:
		for line in f:
			i = json.loads(line)
			interm_output = []
			interests = str(i["interests"])
			for k in automations:
				interm_output.extend(matchKeywordsWithAutomation(automations[k], interests))
			output[str(i["name"])] = interm_output
	return output

'''
Return .meld-style statements in string that connects the event identifier symbol with known faculty interests.
For every term contributed by the faculty, it also pulls in all generalized terms of it. For example, if the faculty member contributes the term 'network architecture', then 'networks' and 'computer science' will also be included. The terms from this example is drawn from the taxonomy file 'concept_hierarchy_cs.txt'.
'''
def get_possible_relevant_topics_from_host_interests(faculty_name, title, facultyInterestDict, expander):
	output_txt = ''
	if faculty_name is not None:
		res = facultyInterestDict[faculty_name]
		final_topics = set()
		for r in res:
			final_topics.add(r.lower())
			if expander is not None:
				matches = expander['interests'][r.lower()]
				for m in matches:
					final_topics.add(m.lower())
		for m in final_topics:
			txt = re.sub('[ \t/]+', '', m.title())+'-topic'
			output_txt += '(hasPossibleTopic {} {})\n'.format(title,txt) 
	return output_txt

'''
Concatenate the event title and abstract and match keywords on the result. 
The matched terms will pull in all generalized terms of it. For example, if the term 'network architecture' is matched, then 'networks' and 'computer science' will also be included. The terms from this example is drawn from the taxonomy file 'concept_hierarchy_cs.txt'.
'''
def matchEventTopics(automatons, expander, topic_type, entry_format_string, topic_sufix, title, abstract):
	string = str((title + abstract).lower())
	output_txt = ''
	if entry_format_string is None:
		entry_format_string = '(isRelevantTo {} {})\n'
	if topic_sufix is None:
		topic_sufix = ''
	for k in automatons:
		needles = matchKeywordsWithAutomation(automatons[k], string)
		res = [toFullTerms(topic_type, x) for x in needles]
		if len(res):
			final_topics = set()
			for r in res:
				final_topics.add(r.lower())
				if expander is not None:
					matches = expander[topic_type][r.lower()]
					for m in matches:
						final_topics.add(m.lower())
			for m in final_topics:
				txt = re.sub('[ \t/]+', '', m.title())+topic_sufix
				output_txt += entry_format_string.format(title,txt) # '(isRelevantTo {} {})\n'.format(title, txt)
	return output_txt

#################################################
### Interests Specific Utilities

def setup_automations(rebuildKeywords):
	return createAutomationsForInterests(rebuildKeywords)

def setup_faculty_interests(automations):
	return getCuratedFacultyInterestList(automations, 'manually_curated_faculty_interests.jl')

def setup_interest_topic_matching(isRebuild):
	inputs = ['concept_hierarchy_cs.txt', 'concept_hierarchy_ce.txt', 
	  		'concept_hierarchy_ee.txt', 'concept_hierarchy_math.txt',
	  		'concept_hierarchy_other.txt','concept_hierarchy_additional.txt']
	return setup_topic_expander('interests', inputs, 'interest_keyword_dump.txt', isRebuild)

def setup_topic_expander(domain, inputs, file_name, isRebuild):	
	if isRebuild or not os.path.isfile(data_directory+file_name):
		iar.reloadKeyWords(inputs,file_name)
	output = {}
	with open(data_directory + file_name) as expander_file:
		for line in expander_file:
			l = json.loads(line)
			if domain not in output:
				output[domain] = {}
			output[domain][l['entry']] = l['related']
	return output

def setup_abbreviation_resolver(domain, file_name, output):
	if domain not in output:
		output[domain] = {}
	with open(data_directory+file_name) as resolver:
		for line in resolver:
			terms = line.rstrip('\r\n').split('\t')
			output[domain][terms[0]] = terms[1]
	return output

'''
Recreate all interests parts of the interests module from scratch. Must be done after editing the taxonomy, abbreviation, or faculty interests files after the interests module is booted.
'''
def reload():
	abbreviationResolver = setup_abbreviation_resolver('interests', 'abbreviations.txt',{})
	automations = setup_automations(True)
	matchedFacultyInterests = setup_faculty_interests(automations)
	interestExpansion = setup_interest_topic_matching(True)

automations = setup_automations(False)
matchedFacultyInterests = setup_faculty_interests(automations)
interestExpansion = setup_interest_topic_matching(False) # domain, keyword, related keywords
abbreviationResolver = setup_abbreviation_resolver('interests', 'abbreviations.txt',{})

#################################################
### Interest Processing

'''
Creates a .meld-style string that connects all topics of interests to the event. 
If a desirable match is not found, please update the training data files.
'''
def get_meld_string(faculty_name, event_name, event_desc):
	event_title = re.sub('[ \t/]+', '', event_name.title())+'-Event'
	output_txt = '(in-microtheory NuEventMt)\n'
	try:
		output_txt += get_possible_relevant_topics_from_host_interests(faculty_name, event_title, matchedFacultyInterests, interestExpansion)
	except Exception as e:
		print(e)
	try:
		output_txt += matchEventTopics(automations, interestExpansion, 'interests', '(isRelevantTo {} {})\n', '-topic', event_title, event_desc)
	except Exception as e:
		print(e)
	return output_txt

#################################################
### Interest Processing From JSON Query String

'''
Take a JSON string in the form of: 
{"faculty":"<name>","title":"<title>","desc":"<abstract>"[,"save_path":"<path/name>"]}
And calls get_meld_string with its content. If "save_path" is specified, the .meld-style string will be saved as a meld file in the location specified.
'''
def process_json_request(json_in_text):
	json_coll = json.loads(json_in_text)
	faculty = json_coll['faculty'] if 'faculty' in json_coll else None
	title = json_coll['title'] if 'title' in json_coll else None
	desc = json_coll['desc'] if 'desc' in json_coll else None
	save_loc_name = json_coll['save_path'] if 'save_path' in json_coll else None
	response_txt = None
	if save_loc_name is not None:
		meld = get_meld_string(faculty, title, desc)
		with open(save_loc_name, 'w') as out_file:
			out_file.write(meld)
		response_txt = 'Meld output saved to: ' + save_loc_name + '\n'
	else:
		response_txt = get_meld_string(faculty, title, desc)
	return response_txt

#################################################
### Special Topics 

'''
Code in this section extends the interest matching capability to other keyword matching scenarios with similar output requirement. This is not part of the main deliverables but it might be useful for others in the future. The function "demo_specialty_meld_string" contains a demo of how to use it. 
'''

special_automations = {}
special_topic_meld_head = {}
special_topic_event_trail = {}
special_topic_expander = {}
special_topic_entry_format = {}
special_topic_entry_suffix = {}

def add_automation(domain, name, concept_hierarchy_txt):
	reconstructConceptList(concept_hierarchy_txt)
	special_automations[domain] = createSingleAutomation('list_form_'+concept_hierarchy_txt)

def add_special_topics(domain, special_header, special_event_trail):
	special_topic_meld_head[domain] = special_header
	special_topic_event_trail[domain] = special_event_trail

def add_special_topics_expander(domain, inputs, output_file_name, isReload):
	special_topic_expander.update(setup_topic_expander(domain, inputs, output_file_name, isReload))

def add_entry_format_and_suffix(domain, format_string, suffix):
	special_topic_entry_format[domain] = format_string
	special_topic_entry_suffix[domain] = suffix

def get_specialty_meld_string(domain, event_name, event_desc):
	# processing
	event_title = re.sub('[ \t/()&,]+', '', event_name.title())+special_topic_event_trail[domain]
	output_txt = special_topic_meld_head[domain]
	try:
		output_txt += matchEventTopics(special_automations, special_topic_expander, domain, \
			special_topic_entry_format[domain], special_topic_entry_suffix[domain], event_title, event_desc)
	except Exception as e:
		print(e)
	return output_txt

def demo_specialty_meld_string():
	add_automation('food','a_food','concept_hierarchy_food.txt')
	add_special_topics('food','(in-microtheory NuEventMt)\n','-Event')
	add_special_topics_expander('food', ['concept_hierarchy_food.txt'], 'food_keyword_dump.txt', True)
	add_entry_format_and_suffix('food', '(hasFoodType {} {})\n', '-FoodTag')
	return get_specialty_meld_string('food', 'EECS FREE Bagels & Coffee in the Ford 3rd floor Student Lounge (SW corner), Fri 6/1', 'Please join GEECS and EECS for free Panera bagels and gourmet coffee Friday, 6/1 @ 9:30 am in the Ford 3rd floor Student Lounge (SW corner). We look forward to seeing you!')


#################################################
### Demos

def main():
	reload()
	print(get_meld_string('Ken Forbus', 'Machines As Thought Partners', 'AI systems should not only propose solutions or answers but also explain why they make sense. Statistical machine learning is a powerful tool for discovering patterns in data, but, Dr. Ferrucci asks, can it produce understanding or enable humans to justify and take reasoned responsibility for individual outcomes? Dr. Ferrucci will also include an overview of Elemental Cognition, his company that is focused on creating AI systems that autonomously learn from human language and interaction to become powerful and fluent thought partners that facilitate complex decision making. Specifically, Elemental Cognition investigates a future in which AI is a powerful amplifier of human creativity-a system that leverages statistical machine learning but focuses primarily on a type of learning that enables humans and machines to share an understanding and collaborate on exploring the question, "Why?"'))

	print(process_json_request('{"faculty":"Ken Forbus","title":"Machines As Thought Partners","desc":"AI systems should not only propose solutions or answers but also explain why they make sense. Statistical machine learning is a powerful tool for discovering patterns in data, but, Dr. Ferrucci asks, can it produce understanding or enable humans to justify and take reasoned responsibility for individual outcomes? Dr. Ferrucci will also include an overview of Elemental Cognition, his company that is focused on creating AI systems that autonomously learn from human language and interaction to become powerful and fluent thought partners that facilitate complex decision making. Specifically, Elemental Cognition investigates a future in which AI is a powerful amplifier of human creativity-a system that leverages statistical machine learning but focuses primarily on a type of learning that enables humans and machines to share an understanding and collaborate on exploring the question, \\"Why?\\""}'))
	
	print(demo_specialty_meld_string())

if __name__ == "__main__":
	main()
