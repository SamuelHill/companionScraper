import os.path
import ahocorasick

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
	for end_index, (insert_order, original_value) in A.iter(haystack):
		start_index = end_index - len(original_value) + 1
		print((start_index, end_index, (insert_order, original_value)))
		assert haystack[start_index:start_index + len(original_value)] == original_value

def runEverythingThrough(title, abstract):
	print 
	print title
	haystack = str((title + abstract).lower())
	print 'CS: '
	findTheNeedles(A_cs, haystack)
	print 'CE: '
	findTheNeedles(A_ce, haystack)
	print 'EE: '
	findTheNeedles(A_ee, haystack)

A_cs = getAutomation('../inputs/concept_list_cs.txt')
A_ce = getAutomation('../inputs/concept_list_ce.txt')
A_ee = getAutomation('../inputs/concept_list_ee.txt')


runEverythingThrough('Ultra-Low Power IC Design 101', 'This talk describes recent progress in ultra-low power (ULP) circuit and system design, with application to IoT and wireless sensing microsystems. Specific circuit topics include relaxation oscillators, digital logic/sequentials, power management including energy harvesting, memories, and interface circuits. Key barriers to miniaturization of such microsystems are also described, with potential solutions.')

runEverythingThrough('Enabling Data Science for the Majority', 'Despite great strides in the generation, collection, storage, and processing of data at scale, data science is either out of reach, or, at the very least, extremely inconvenient for the majority of the population. The driving goal of our research is to help individuals and teams--regardless of programming or analysis ability--manage, analyze, make sense of, and draw insights from large datasets. Over the past three years, we\'ve been building (with collaborators at MIT, UMD, and UChicago) a number of tools that empower individuals and teams to perform data science more effectively and effortlessly. These tools span the spectrum of data science or analysis needs, all the way from extracting data into a form amenable to analysis, to exploration and derivation of insights, to recording and sharing of datasets and insights. These tools include DataSpread, a "big data" spreadsheet tool that combines the benefits of spreadsheets and databases; ZenVisage, a visual exploration tool that facilitates the rapid discovery of trends or patterns; and Orpheus, a collaborative data analytics tool that enables the efficient recording and retrieval of dataset versions at various stages of analysis. All of our tools are open-source, and have witnessed usage in fields such as neuroscience, battery science, genomics, astrophysics, marketing analytics, and ad analytics. In my talk, I will argue that the development of such tools needs to (i) crucially minimize the effort, time, and complexity on the part of the human analyst, (ii) draw on techniques from multiple disciplines--databases, data mining, and interaction, and (iii) revisit the design of all layers of the software stack, from interfaces and interactions, to query languages and APIs, to query execution and optimization, and finally to representation, storage and indexing. Drawing on examples from the tools that we\'ve developed, I will describe how a first-principles approach can lead to solutions that yield practical benefits in terms of scalability, interactivity, usability, and accuracy, while also providing theoretical guarantees. I will finally outline a future research agenda for tool development to truly democratize data science, with the ultimate goal of allowing everyone to tap into the hidden potential in their datasets at scale.')

runEverythingThrough('Detecting & Preventing Vulnerabilities Using Program Analysis & Deep Learning', 'Software and hardware vulnerabilities are a long standing security problem. In this talk, I will present two of my works on detecting and preventing vulnerabilities. First, I will introduce my work on trace oblivious computation, which uses programming language techniques to enable efficient secure computation over multiple parties\' sensitive data in the presence of strong attackers who can observe a program\'s execution trace, such as memory access addresses. My work focuses on both theoretical development to formally enforce a program is free of vulnerabilities to leak information through such execution traces, as well as practical system building to yield the state-of-the-art performance. Second, I will introduce my work to use deep learning approaches to solve the binary code similarity detection problem. Code similarity detection has many applications such as plagiarism and vulnerability detection; however, I will show that whether two pieces of code are similar cannot be defined as one common criteria for all applications. My work is the first to demonstrate that deep learning can be used to mitigate this issue so that the same approach can be applied for different application domains; also our learning-based approach outperforms the best heuristics-based approach by a large margin. My research interest lies at the intersection of security, programming languages, and deep learning. I will briefly introduce my other efforts in this broad area and discuss potential future directions.')

