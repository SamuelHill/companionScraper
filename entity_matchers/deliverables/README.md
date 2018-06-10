# Interests Module

Overview 
--------

The interests module creates .meld-style strings that associate events with the topics they touch on. Tailored to process EECS seminar events, it conducts keyword spotting from the title and abstract of the semniar. To boost its effectiveness, the system appends the research interests of the event host if it is a known EECS faculty member.

The keyword spotting can be repurposed to match other types of topics. An example of how to repurpose the module to spot food items from an event description (bagel and coffee) is included in the code. 


Installation Instruction (Windows)
----------------------------------

1. Download 64-bits Miniconda Windows Installer for Python 3.6 from *https://conda.io/miniconda.html*
2. Install Miniconda from the installer -- make sure to check **Add Anaconda to my PATH environment variable** when prompted
3. In the **Start Menu**, open **Anaconda Prompt** and install dependency with command **conda install -c conda-forge pyahocorasick**


Demo Instruction
----------------

1. In **Anaconda Prompt**, navigate to the directory containing this document, make sure you have the following files:
  * api_python3_writers.py
  * api_python3_interests_and_related.py
  * api_python3_ahocorasick.py
  * data/abbreviations.txt
  * data/concept_hierarchy_additional.txt
  * data/concept_hierarchy_ce.txt
  * data/concept_hierarchy_cs.txt
  * data/concept_hierarchy_ee.txt
  * data/concept_hierarchy_food.txt
  * data/concept_hierarchy_math.txt
  * data/manually_curated_faculty_interests.jl
2. Since the interests module is only a library, the main function in **api_python3_ahocorasick.py** serves as a demo. To run it, issue command **python api_python3_ahocorasick.py**


Glossary
--------

### Python Scripts Included

* api_python3_interests_consolidator.py
* api_python3_writers.py
* api_python3_interests_and_related.py
* api_python3_ahocorasick.py


### Software Package Dependencies

* pyahocorasick
* (OPTIONAL) lxml


### Text Input File Dependencies

* abbreviations.txt
* concept_hierarchy_additional.txt
* concept_hierarchy_ce.txt
* concept_hierarchy_cs.txt
* concept_hierarchy_ee.txt
* concept_hierarchy_food.txt
* concept_hierarchy_math.txt
* manually_curated_faculty_interests.jl
* (OPTIONAL) ccs_flat.cfm.html


### Referenced Algorithm

The interests module uses the *Aho-Corasick (AC)* keyword spotting algorithm. It takes a list of words as its targets and search a given string to report the presence of those words. 


Data
----

There are three sources of training data: curated faculty interests, abbreviation dictionary, keyword taxonomy forests. 

The curated faculty interests is a collection of faculty interests manually created from the EECS Undergraduate Student Manual. It is stored in JSON Line format in **manually_curated_faculty_interests.jl**. Each line in the file is a JSON object, including the name of a professor and a list of keywords that best describe his/her interests. 

Abbreviation dictionary is simply pairs of abbreviations and their original forms separated by tabs. Note that all abbreviations are preceded by a single space character. AC does not tokenize the query string before matching. Instead, it is used to efficiently match character sequences to character sequences. A space in front of terms like **"AI"** prevents finding a match from string **"computer-aided design for vlsi"**. This spacing trick is used throughout the topic processing pipeline. 

The keyword taxonomy forests are text files with the name *concept_hierarchy_[tag].txt*. Each file contains a taxonomy of concepts (keywords) in a certain topic, such as CS (Computer Science). Each line in a file denotes a topic, and the level of specifity is signified by the number of tab characters before it. Each topic is a specification of the first topic above that has one tab less in the front. 

The keyword taxonomy is used in two ways: it provides training data for AC, and it provides a lineage of topic generalization for any keyword found by AC. For example, suppose AC found the term *Network architecture*. By following the information provided by the file *concept_hierarchy_cs.txt*, we can identify pull out all the terms that generalizes above the term: *Networks* and *Computer Science*. 

To modify the training data, one could edit or simply append more information to the taxonomy files. In case the taxonomy files are lost, one could recover them the original source by:
1. Download the webpage https://dl.acm.org/ccs/ccs_flat.cfm file to **data/ccs_flat.cfm.html**
2. run **api_python3_interest_consolidator.py** to get a large taxonomy that spans all EECS topics
3. (OPTIONAL) Manually divide the taxonomy by genre (CS, EE, etc.)



Bonus
-----

Try server mode: 
1. Boot the server in one Anaconda Prompt with command **python python3_http_server.py**
2. In a separate Anaconda Prompt, enter the following cURL query:
```
curl localhost:8081/event_interests -H "Content-Type: application/json" -d "{\"faculty\":\"Ken Forbus\",\"title\":\"Machines As Thought Partners\",\"desc\":\"AI systems should not only propose solutions or answers but also explain why they make sense. Statistical machine learning is a powerful tool for discovering patterns in data, but, Dr. Ferrucci asks, can it produce understanding or enable humans to justify and take reasoned responsibility for individual outcomes? Dr. Ferrucci will also include an overview of Elemental Cognition, his company that is focused on creating AI systems that autonomously learn from human language and interaction to become powerful and fluent thought partners that facilitate complex decision making. Specifically, Elemental Cognition investigates a future in which AI is a powerful amplifier of human creativity-a system that leverages statistical machine learning but focuses primarily on a type of learning that enables humans and machines to share an understanding and collaborate on exploring the question, \\\"Why?\\\"\"}"
```