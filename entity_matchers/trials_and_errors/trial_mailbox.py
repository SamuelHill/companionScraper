import mailbox
import re

mbox = mailbox.mbox('../inputs/seanoconnor.mbox')

i = 10
for message in mbox:
	extracted_message = None
	if message.is_multipart():
		# content = ''.join(part.get_payload(decode=True) for part in message.get_payload())
		for part in message.walk():
			ctype = part.get_content_type()
			cdispo = str(part.get('Content-Disposition'))
			# skip any text/plain (txt) attachments
			if ctype == 'text/plain' and 'attachment' not in cdispo:
				body = part.get_payload(decode=True)  # decode
				extracted_message = re.sub('(?<=[ @.a-zA-Z0-9])[\r][\n](?=[ @.a-zA-Z0-9])', ' ', body)
				print extracted_message
				break
	else:
		extracted_message = message.get_payload(decode=True)
		print extracted_message
	if i > 0:
		i-=1
	else:
		break