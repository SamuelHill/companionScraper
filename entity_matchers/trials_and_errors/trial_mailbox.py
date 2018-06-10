import mailbox
import re

def processSubject(found_messages, message):
	extracted_subject = None
	
	email_subject = re.sub('[\r\n]+', ' ', message['subject'])
	
	# observation: computer science subject is usually quoted
	temp = re.search('["].+["]', email_subject) 
	if temp is not None:
		subject = re.sub('[ \t]+', ' ', temp.group(0)[1:-1])
		if subject not in found_messages:
			found_messages[subject] = None
			extracted_subject = subject
	return extracted_subject

def processMessage(extracted_message):
	# print extracted_message
	abstract = None
	temp = re.search(r'(?<=Abstract: )[- ,.@<>\'\"/\\a-zA-Z0-9\(\)\[\]\$%#\*\^]+', extracted_message)
	if temp is not None:
		abstract = temp.group(0)

	return abstract

def processFirstCoupleOfMessages(mbox, i):
	found_messages = {}
	for message in mbox:
		extracted_message = None
		extracted_subject = processSubject(found_messages, message)
		if extracted_subject is None:
			continue
		# continue

		if message.is_multipart():
			# content = ''.join(part.get_payload(decode=True) for part in message.get_payload())
			for part in message.walk():
				ctype = part.get_content_type()
				cdispo = str(part.get('Content-Disposition'))
				# skip any text/plain (txt) attachments
				if ctype == 'text/plain' and 'attachment' not in cdispo:
					body = part.get_payload(decode=True)  # decode
					extracted_message = re.sub('(?<=[ @.a-zA-Z0-9])[\r][\n](?=[ @.a-zA-Z0-9])', ' ', body)
					break
		else:
			extracted_message = message.get_payload(decode=True)

		if extracted_subject is not None:
			abstract = processMessage(extracted_message)
			if abstract is None:
				del found_messages[extracted_subject]
			else:
				i -= 1
				found_messages[extracted_subject] = abstract

		if i == 0:
			break 
			# return re.sub('[\r][ \t\r\n]+', '\t', extracted_message)
	return found_messages

###########################################
### Go through the first 5 letters, return the last one

mbox = mailbox.mbox('../inputs/seanoconnor.mbox')
found_messages = processFirstCoupleOfMessages(mbox, 100)

doc_complete = []

for key, value in found_messages.iteritems():
	doc_complete.append(str(key + '	' + value))

print '[INFO] doc_complete has %d document entries\n' % (len(doc_complete))


import nltk
import string

nltk.download('stopwords')
from nltk.corpus import stopwords 

nltk.download('wordnet')
from nltk.stem.wordnet import WordNetLemmatizer



stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

doc_clean = [clean(doc).split() for doc in doc_complete]

# Importing Gensim
import gensim
from gensim import corpora

# Creating the term dictionary of our courpus, where every unique term is assigned an index. 
dictionary = corpora.Dictionary(doc_clean)

# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]


# Creating the object for LDA model using gensim library
Lda = gensim.models.ldamodel.LdaModel

# Running and Trainign LDA model on the document term matrix.
ldamodel = Lda(doc_term_matrix, num_topics=50, id2word = dictionary, passes=200)


print(ldamodel.print_topics(num_topics=50, num_words=10))