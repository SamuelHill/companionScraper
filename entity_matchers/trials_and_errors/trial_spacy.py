import spacy

# remember to remove:     
# /Library/Python/2.7/site-packages/en_core_web_lg -->
# /var/root/Library/Python/2.7/lib/python/site-packages/spacy/data/en_core_web_lg
# /Library/Python/2.7/site-packages/en_core_web_sm -->
# /var/root/Library/Python/2.7/lib/python/site-packages/spacy/data/en

test_1 = True
test_2 = False
test_3 = True
test_4 = True
test_5 = True

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')

def process(nlp, text):
	doc = nlp(text)
	for entity in doc.ents:
	    print(entity.text, entity.label_)
	print

if test_1:
	# Process whole documents
	text = (u"When Sebastian Thrun started working on self-driving cars at "
	        u"Google in 2007, few people outside of the company took him "
	        u"seriously. I can tell you very senior CEOs of major American "
	        u"car companies would shake my hand and turn away because I wasn't "
	        u"worth talking to,\" said Thrun, now the co-founder and CEO of "
	        u"online higher education startup Udacity, in an interview with "
	        u"Recode earlier this week.")
	process(nlp, text)

if test_2:
	# Event description
	text = (u"Despite the continued development of individual technologies and processes for supporting human endeavors, major leaps in solving complex human problems will require advances in system-level thinking and orchestration. In this talk, I describe efforts to design, build, and study Computational Ecosystems that interweave community process, social structures, and intelligent systems to unite people and machines to solve complex problems and advance human values at scale. Computational ecosystems integrate various components to support ecosystem function; the interplay among components synergistically advances desired values and problem solving goals in ways that isolated technologies and processes cannot. Taking a systems approach to design, computational ecosystems emphasize (1) computational thinking to decompose and distribute problem solving to diverse people or machines most able to address them; and (2) ecological thinking to create sustainable processes and interactions that support jointly the goals of ecosystem members and proper ecosystem function. I present examples of computational ecosystems designed to advance community-based planning and research training, that respectively engages thousands of people in planning an event and empowers a single faculty member to provide authentic research training to 20+ students. These solutions demonstrate how to combine wedges of human and machine competencies into integrative technology-supported, community-based solutions. I will preview what's ahead for computational ecosystems, and close with a few thoughts on the role of computing technologies in advancing human values at scale.")
	nlp2 = spacy.load('en_core_web_lg')
	process(nlp2, text)

if test_3:
	# Process whole documents
	text = (u"Much of AI today is deployed in the Cloud primarily due to the high complexity of machine learning algorithms. Realizing inference functionality on sensory Edge devices requires one to find ways to operate at the other edge, i.e., at the limits of energy efficiency, latency, and accuracy, in nanoscale semiconductor technologies. This talk will describe the Shannon-inspired statistical computing framework developed by researchers in the SONIC Center (2013-17), to accomplish this objective. This framework comprises low signal-to-noise ratio (SNR) circuit fabrics (the channel) with engineered error statistics, coupled with efficient techniques to compensate for computational errors (encoder and decoder). A low SNR circuit fabric referred to as deep in-memory architecture (DIMA) will be described. DIMA breaches the long-standing \"memory wall\" in von Neumann architectures by embedding analog computations in the periphery of the memory array (see https://spectrum.ieee.org/computing/hardware/to-speed-up-ai-mix-memory-and-processing) thereby achieving >100X energy-delay-product gains in laboratory prototypes over custom digital architectures implementing the same inference function. The strong systems-to-devices connection inherent in Shannon-inspired statistical computing creates an opportunity for researchers in machine learning, computer architecture, integrated circuits, and nanoscale devices, to work together to design intelligent machines of the future. The talk will end with a discussion of future directions.")
	process(nlp, text)

if test_4:
	# Process whole documents
	text = (u"Controlling Domain Wall Dynamics by Interface Engineering in Ultra-Thin Films with Perpendicular Magnetic Anisotropy")
	process(nlp, text)
	text = (u"One crucial breakthrough in spin electronics has recently been achieved regarding the possibility to move magnetic domain walls (DWs) in magnetic tracks using the sole action of an electrical current instead of a conventional magnetic field. Here, we will focus on the possibility to control precisely DW motion from the creep to the flow regime through interface engineering. Particularly, in order to increase DW velocity, it is crucial to better understand the relative effect of interface anisotropy and interface disorder on domain wall motion. This will be demonstrated using different strategies based on electric field effect to control interface anisotropy and He+ ion irradiation induced intermixing to manipulate interface disorder. We will show that even a low interface disorder has a strong influence on DW dynamics. Finally, we will demonstrate that edge damages induced by the patterning process can also strongly affect DW dynamics in narrow wires.")
	process(nlp, text)

if test_5:
	text = (u"Human-Centric Machine Learning: Enabling Machine Learning for High-Stakes Decision-Making")
	process(nlp, text)
	text = (u"Domains such as law, healthcare, and public policy often involve highly consequential decisions which are predominantly made by human decision-makers. The growing availability of data pertaining to such decisions offers an unprecedented opportunity to develop machine learning models which can aid human decision-makers in making better decisions. However, the applicability of machine learning to the aforementioned domains is limited by certain fundamental challenges: 1) The data is selectively labeled i.e., we only observe the outcomes of the decisions made by human decision-makers and not the counterfactuals. 2) The data is prone to a variety of selection biases and confounding effects. 3) The successful adoption of the models that we develop depends on how well decision-makers can understand and trust their functionality, however, most of the existing machine learning models are primarily optimized for predictive accuracy and are not very interpretable. In this talk, I will describe novel computational frameworks which address the aforementioned challenges, thus, paving the way for large-scale deployment of machine learning models to address problems of significant societal impact. First, I will discuss how to build interpretable predictive models and explanations of complex black box models which can be readily understood and consequently trusted by human decision-makers. I will then outline efficient and provably near-optimal approximation algorithms to solve these problems. Next, I will present a novel evaluation framework which allows us to reliably compare the quality of decisions made by human decision-makers and machine learning models amidst challenges such as missing counterfactuals and presence of unmeasured confounders (unobservables). Lastly, I will provide a brief overview of my research on diagnosing and characterizing biases (systematic errors) in human decisions and predictions of machine learning models. I will conclude the talk by sketching future directions which enable effective and efficient collaboration between humans and machine learning models to address problems of societal impact.")
	process(nlp, text)

# Determine semantic similarities
# doc1 = nlp(u"my fries were super gross")
# doc2 = nlp(u"such disgusting fries")
# similarity = doc1.similarity(doc2)
# print(doc1.text, doc2.text, similarity)