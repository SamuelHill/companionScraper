import json
import codecs
import sys
# sys.path.append('..')
import Writers


# data = []
# with codecs.open('inputs/curated_faculty_interests.jl', mode='r', encoding='ascii') as f:
#	 for line in f:
#	 i = json.loads(line)
#	 # print i
#	 print i["name"], i["interests"]


def processDoc(output, relative_file_path):
	with codecs.open(relative_file_path, mode='r', encoding='ascii') as f:
		previous_level = 0
		last_list = []
		last = None
		for line in f:
			ls = line.lstrip('\t')
			current_level = len(line) - len(ls)
			ls = ls.strip('\n\t')
			if current_level > previous_level:
				last_list.append(last)
			elif current_level < previous_level:
				diff = previous_level - current_level
				for i in range(0, diff):
					last_list.pop()
			if ls not in output:
				output[ls] = {}
				output[ls][ls] = set(last_list)
			else:
				output[ls][ls].update(set(last_list))
			last = ls
			previous_level = current_level

def appendTermsMappingToFile(relative_output_file_path, relative_input_file_paths):
	output = {}

	for rel in relative_input_file_paths:
		processDoc(output, rel)

	# for k in output:
	# 	print output[k]

	writer = Writers.JSONWriter()

	output2 = ''
	for k in output:
		writer.start()
		writer.entry("entry",k)
		writer.header("related")
		writer.startCluster()
		for e in output[k][k]:
			writer.text(e)
		writer.endCluster()
		writer.end()
		output2 += writer.output() + '\n'
		writer.clear()

	with open(relative_output_file_path, 'w') as outfile:
		outfile.write(output2)



def loadTermsMappingFromFile(relative_file_path):
	output = {}
	with codecs.open(relative_file_path, mode='r', encoding='ascii') as f:
		for line in f:
			i = json.loads(line)
			output[str(i["entry"])] = [str(x) for x in i["related"]]
	return output

def reloadKeyWords():
	inputs = ['inputs/concept_hierarchy_cs.txt', 'inputs/concept_hierarchy_ce.txt', 'inputs/concept_hierarchy_ee.txt', 'inputs/concept_hierarchy_math.txt']
	appendTermsMappingToFile('inputs/interest_keyword_dump.txt', inputs)

def main():
	reloadKeyWords()

if __name__ == "__main__":
	main()

# print loadTermsMappingFromFile('inputs/interest_keyword_dump.txt')