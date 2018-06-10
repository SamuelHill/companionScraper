# Source: https://gist.github.com/alexbowe/879414
# pip install https://pypi.python.org/packages/source/n/nltk/nltk-3.0.4.tar.gz

from __future__ import print_function
import nltk
import time

### env setup

download_parts = False
if download_parts:
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_treebank_pos_tagger')
    nltk.download('stopwords')

### Prep

sentence_re = r'''(?x)      # set flag to allow verbose regexps
        (?:[A-Z]\.)+        # abbreviations, e.g. U.S.A.
      | \w+(?:-\w+)*        # words with optional internal hyphens
      | \$?\d+(?:\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
      | \.\.\.              # ellipsis
      | [][.,;"'?():_`-]    # these are separate tokens; includes ], [
    '''

lemmatizer = nltk.WordNetLemmatizer()
# stemmer = nltk.stem.porter.PorterStemmer()

#Taken from Su Nam Kim Paper...
grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*><VBG.*>?}  # Nouns and Adjectives, terminated with Nouns, perhaps followed with verb-ing
 
    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc... # this does not work unless placed before the first
"""
chunker = nltk.RegexpParser(grammar)


### Process 

from nltk.corpus import stopwords
stopwords = stopwords.words('english')

def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter = lambda t: t.label() == 'NP'):
        yield subtree.leaves()

def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it."""
    word = word.lower()
    # word = stemmer.stem_word(word) # avoid stemming
    word = lemmatizer.lemmatize(word)
    return word

def acceptable_word(word):
    """Checks conditions for acceptable word: length, stopword."""
    accepted = bool(2 <= len(word) <= 40
        and word.lower() not in stopwords)
    return accepted

def get_terms(tree):
    for leaf in leaves(tree):
        term = [ normalise(w) for w,t in leaf if acceptable_word(w) ]
        yield term

### Output

def groupTermsInString(terms):
    output = ''
    started = False
    for term in terms:
        if not started:
            started = True
        else:
            output += ', '
        startedIn = False
        for word in term:
            if not startedIn:
                startedIn = True
            else:
                output += ' '
            output += word
    return output


### production

def produceOneString(text):
    start_t = time.time()
    toks = nltk.regexp_tokenize(text, sentence_re)
    postoks = nltk.tag.pos_tag(toks)
    # print(postoks)
    tree = chunker.parse(postoks)
    terms = get_terms(tree)
    ret = groupTermsInString(terms)
    end_t = time.time()
    print("\nTime lapsed: %f" % (end_t - start_t))
    return ret

def main():
    text = """Fast, Just-in-time Queries on Heterogeneous Raw Data --- Today\'s scientific and business processes heavily depend on fast and accurate data analysis. Data scientists are routinely overwhelmed by the effort needed to manage the volumes of data produced. As general-purpose data management software is often inefficient, hard to manage, or too generic to serve today\'s applications, businesses increasingly turn to specialised data management software, which can only handle one data format, and then resort to data integration solutions. With the exponential growth of dataset size and complexity, however, data format-specific solutions no longer scale for efficient analysis, thereby slowing down the cycle of analysing and understanding the data, and making decisions. I will illustrate the different nature of problems we face when managing heterogeneous datasets, and how these translate to fundamental challenges for the data management community. Then I will introduce new technologies inspired by these challenges, which overturn long-stangding assumptions, enable meaningful and timely results, and advance discovery."""
    print(produceOneString(text))
    text = """Enabling Data Science for the Majority --- Despite great strides in the generation, collection, storage, and processing of data at scale, data science is either out of reach, or, at the very least, extremely inconvenient for the majority of the population. The driving goal of our research is to help individuals and teams--regardless of programming or analysis ability--manage, analyze, make sense of, and draw insights from large datasets. Over the past three years, we\'ve been building (with collaborators at MIT, UMD, and UChicago) a number of tools that empower individuals and teams to perform data science more effectively and effortlessly. These tools span the spectrum of data science or analysis needs, all the way from extracting data into a form amenable to analysis, to exploration and derivation of insights, to recording and sharing of datasets and insights. These tools include DataSpread, a "big data" spreadsheet tool that combines the benefits of spreadsheets and databases; ZenVisage, a visual exploration tool that facilitates the rapid discovery of trends or patterns; and Orpheus, a collaborative data analytics tool that enables the efficient recording and retrieval of dataset versions at various stages of analysis. All of our tools are open-source, and have witnessed usage in fields such as neuroscience, battery science, genomics, astrophysics, marketing analytics, and ad analytics. In my talk, I will argue that the development of such tools needs to (i) crucially minimize the effort, time, and complexity on the part of the human analyst, (ii) draw on techniques from multiple disciplines--databases, data mining, and interaction, and (iii) revisit the design of all layers of the software stack, from interfaces and interactions, to query languages and APIs, to query execution and optimization, and finally to representation, storage and indexing. Drawing on examples from the tools that we\'ve developed, I will describe how a first-principles approach can lead to solutions that yield practical benefits in terms of scalability, interactivity, usability, and accuracy, while also providing theoretical guarantees. I will finally outline a future research agenda for tool development to truly democratize data science, with the ultimate goal of allowing everyone to tap into the hidden potential in their datasets at scale. """
    print(produceOneString(text))


if __name__ == "__main__":
    main()