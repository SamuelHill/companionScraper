from unidecode import unidecode

def cleanHTML(content, isDecode = False):
	if isDecode is True:
		cleaned_content = content.decode('utf-8')
	else:
		cleaned_content = content
	if '\t' in cleaned_content:
		cleaned_content=cleaned_content.replace('\t','\\t')
	if '\r' in cleaned_content:
		cleaned_content=cleaned_content.replace('\r','\\r')
	if '\n' in cleaned_content:
		cleaned_content=cleaned_content.replace('\n','\\n')
	for ch in ['"', '\xe2\x80\x9d'.decode('utf8'), '\xe2\x80\x9c'.decode('utf8')]:
		if ch in cleaned_content:
			cleaned_content=cleaned_content.replace(ch,'\\' + ch)
	if '\\\\"' in cleaned_content:
		cleaned_content=cleaned_content.replace('\\\\"','\\\\\\"')
	return cleaned_content

def getJSONElementFlat(field_name, entry, is_first_entry = False):
	s = cleanHTML(entry)
	if is_first_entry:
		return u'"' + field_name + u'":"' + s + u'"'
	else:
		return u',"' + field_name + u'":"' + s + u'"'

def getJSONElementArray(field_name, entries, is_first_entry = False):
	json = u''
	if is_first_entry:
		json += u'"' + field_name + u'":[' 
	else:
		json += u',"' + field_name + u'":[' 
	first = True
	for a in entries:
		if first is True:
			first = False
		else:
			json += u','
		s = a.decode('utf-8') if isinstance(a, str) else a
		s = cleanHTML(s)
		json += u'"' + s + u'"'
	json += u']'
	return json

def getJSONListOfPairs(field_name, names, entries, is_first_entry = False):
	json = u''
	if is_first_entry:
		json += u'"' + field_name + u'":{' 
	else:
		json += u',"' + field_name + u'":{' 
	for i in range(0, len(names)):
		if i is 0:
			first = False
		else:
			json += u','
		json += u'"' + names[i] + u'":"' + entries[i] + u'"'
	json += u'}'
	return json