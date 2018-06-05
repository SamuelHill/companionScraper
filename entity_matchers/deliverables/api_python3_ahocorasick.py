import re
import json
import codecs
import os.path
import ahocorasick
import api_python3_interests_and_related as iar

data_directory='data/'

def getAutomation(path):
	A = ahocorasick.Automaton()

	list_txt = open(path, 'r')
	list_split = list_txt.read().lower().split('\t')
	list_txt.close()

	for idx, key in enumerate(list_split):
		A.add_word(key, (idx, key))

	A.make_automaton()
	return A

def findTheNeedles(A, haystack):
	output = set()
	for end_index, (insert_order, original_value) in A.iter(haystack):
		start_index = end_index - len(original_value) + 1
		assert haystack[start_index:start_index + len(original_value)] == original_value
		output.add(original_value)
	return list(output)

def reconstructConceptList(output_file_path, input_file_path):
	output = ''
	with codecs.open(input_file_path, mode='r', encoding='ascii') as f:
		for line in f:
			output += line
	output = re.sub(r'[\t\r\n]+', '\t', output).lower()
	with open(output_file_path, 'w') as o:
		o.write(output)

def createAutomations(is_reconstructing):
	if is_reconstructing or not os.path.isfile(data_directory+'concept_list_cs.txt'):
		reconstructConceptList(data_directory+'concept_list_cs.txt', data_directory+'concept_hierarchy_cs.txt')
		reconstructConceptList(data_directory+'concept_list_ce.txt', data_directory+'concept_hierarchy_ce.txt')
		reconstructConceptList(data_directory+'concept_list_ee.txt', data_directory+'concept_hierarchy_ee.txt')
		reconstructConceptList(data_directory+'concept_list_math.txt', data_directory+'concept_hierarchy_math.txt')
		reconstructConceptList(data_directory+'concept_list_other.txt', data_directory+'concept_hierarchy_other.txt')
		if os.path.isfile(data_directory+'concept_list_additional.txt'):
			reconstructConceptList(data_directory+'concept_list_additional.txt', data_directory+'concept_hierarchy_additional.txt')
	output = {}
	output['CS'] = getAutomation(data_directory+'concept_list_cs.txt')
	output['CE'] = getAutomation(data_directory+'concept_list_ce.txt')
	output['EE'] = getAutomation(data_directory+'concept_list_ee.txt')
	output['Math'] = getAutomation(data_directory+'concept_list_math.txt')
	return output

def matchFacultyInterests(automatons, name, interests):
	haystack = str(interests)
	output = []
	for k in automatons:
		output.extend(findTheNeedles(automatons[k], haystack))
	return output

def toFullTerms(text):
	if text.lower() == 'cs':
		return 'computer science'
	elif text.lower() == 'ce':
		return 'computer engineering'
	elif text.lower() == 'ee':
		return 'electrical engineering'
	elif text.lower() == ' ai':
		return 'artificial intelligence'
	elif text.lower() == ' ml':
		return 'machine learning'
	elif text.lower() == ' hci':
		return 'human-computer interaction'
	elif text.lower() == ' hpc':
		return 'high-performance computing'
	elif text.lower() == ' ic':
		return 'integrated circuit'
	else:
		return text

def matchSeminarTopics(automatons, title, abstract):
	haystack = str((title + abstract).lower())
	output_txt = ''
	for k in automatons:
		needles = findTheNeedles(automatons[k], haystack)
		res = [toFullTerms(x) for x in needles]
		if len(res):
			output_txt += '(isRelevantTo '+title+' '+re.sub('[ \t/]+', '', toFullTerms(k).title())+'-topic)\n'
			for r in res:
				txt = re.sub('[ \t/]+', '', r.title())+'-topic'
				output_txt += '(isRelevantTo '+title+' '+txt+')\n'
	return output_txt

def getCuratedFacultyInterestList(automations, relative_path_of_the_jl_file):
	output = {}
	with codecs.open(relative_path_of_the_jl_file, mode='r', encoding='ascii') as f:
		for line in f:
			i = json.loads(line)
			output[str(i["name"])] = matchFacultyInterests(automations, i["name"], i["interests"])
	return output


def get_possible_relevant_topics_from_host_interests(faculty_name, event_title, facultyInterestDict):
	output_txt = ''
	if faculty_name is not None:
		res = facultyInterestDict[faculty_name]
		for r in res:
			txt = re.sub('[ \t/]+', '', r.title())+'-topic'
			output_txt += '(hasPossibleTopic '+event_title+' '+txt+')\n'
	return output_txt


#################################################
### Setup

def setup_automations(rebuildKeywords):
	# fixed setup
	if rebuildKeywords:
		iar.reloadKeyWords()
	return createAutomations(rebuildKeywords)

def setup_faculty_interests(automations):
	return getCuratedFacultyInterestList(automations, data_directory+'curated_faculty_interests.jl')

automations = setup_automations(True)
matchedFacultyInterests = setup_faculty_interests(automations)

def reload():
	automations = setup_automations(True)
	matchedFacultyInterests = setup_faculty_interests(automations)

#################################################
### Processing

def get_meld_string(automations, matchedFacultyInterests, rebuildKeywords, faculty_name, event_name, event_desc):
	# processing
	event_title = re.sub('[ \t/]+', '', event_name.title())+'-event'
	output_txt = '(in-microtheory NuEventMt)\n'
	output_txt += get_possible_relevant_topics_from_host_interests(faculty_name, event_title, matchedFacultyInterests)
	output_txt += matchSeminarTopics(automations, event_title, event_desc)
	return output_txt

def process_json_request(json_in_text):
    json_coll = json.loads(json_in_text)
    faculty = json_coll['faculty']
    title = json_coll['title']
    desc = json_coll['description']
    response_txt = get_meld_string(automations, matchedFacultyInterests, False, faculty, title, desc)
    return response_txt

def main():
	print(get_meld_string(False, 'Ken Forbus', 'Machines As Thought Partners', 'AI systems should not only propose solutions or answers but also explain why they make sense. Statistical machine learning is a powerful tool for discovering patterns in data, but, Dr. Ferrucci asks, can it produce understanding or enable humans to justify and take reasoned responsibility for individual outcomes? Dr. Ferrucci will also include an overview of Elemental Cognition, his company that is focused on creating AI systems that autonomously learn from human language and interaction to become powerful and fluent thought partners that facilitate complex decision making. Specifically, Elemental Cognition investigates a future in which AI is a powerful amplifier of human creativity-a system that leverages statistical machine learning but focuses primarily on a type of learning that enables humans and machines to share an understanding and collaborate on exploring the question, "Why?"'))

if __name__ == "__main__":
	main()



#################################################
### Demos

# print 'Ken Forbus', matchedFacultyInterests['Ken Forbus']
# print 'Machines As Thought Partners', '---', matchSeminarTopics(automations, 'Machines As Thought Partners', 'AI systems should not only propose solutions or answers but also explain why they make sense. Statistical machine learning is a powerful tool for discovering patterns in data, but, Dr. Ferrucci asks, can it produce understanding or enable humans to justify and take reasoned responsibility for individual outcomes? Dr. Ferrucci will also include an overview of Elemental Cognition, his company that is focused on creating AI systems that autonomously learn from human language and interaction to become powerful and fluent thought partners that facilitate complex decision making. Specifically, Elemental Cognition investigates a future in which AI is a powerful amplifier of human creativity-a system that leverages statistical machine learning but focuses primarily on a type of learning that enables humans and machines to share an understanding and collaborate on exploring the question, "Why?"')

# print 'Jie Gu', matchedFacultyInterests['Jie Gu']
# print 'Ultra-Low Power IC Design 101', '---', matchSeminarTopics(automations, 'Ultra-Low Power IC Design 101', 'This talk describes recent progress in ultra-low power (ULP) IC and system design, with application to IoT and wireless sensing microsystems. Specific circuit topics include relaxation oscillators, digital logic/sequentials, power management including energy harvesting, memories, and interface circuits. Key barriers to miniaturization of such microsystems are also described, with potential solutions.')