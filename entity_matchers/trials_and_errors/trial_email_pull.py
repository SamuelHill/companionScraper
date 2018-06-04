
import smtplib
import time
import imaplib
import email
import base64
import re 

ORG_EMAIL   = "@gmail.com"
FROM_EMAIL  = "usetester767" + ORG_EMAIL
FROM_PWD	= "Test1900"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993

# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------

def read_email_from_gmail():
	try:
		mail = imaplib.IMAP4_SSL(SMTP_SERVER)
		mail.login(FROM_EMAIL,FROM_PWD)
		mail.select('inbox')

		type1, data = mail.search(None, 'ALL')#'(FROM "anjali sinha" SUBJECT "test")')
		mail_ids = data[0]

		id_list = mail_ids.split()   
		first_email_id = int(id_list[0])
		latest_email_id = int(id_list[-1])

		for i in range(latest_email_id,first_email_id - 1, -1):
			typ, data = mail.fetch(i, '(RFC822)' )

			for response_part in data:
				extracted_subject = None
				extracted_message = None
				if isinstance(response_part, tuple):
					msg = email.message_from_string(response_part[1])
					email_subject = re.sub('[\r\n]+', ' ', msg['subject'])
					extracted_subject = re.search('["].+["]', email_subject).group(0)[1:-1]
					email_from = msg['from']
					# print 'From : ' + email_from + '\n'
					# print 'Subject : ' + email_subject + '\n'
					print extracted_subject
					if msg.is_multipart():
						for part in msg.walk():
							ctype = part.get_content_type()
							cdispo = str(part.get('Content-Disposition'))

							# skip any text/plain (txt) attachments
							if ctype == 'text/plain' and 'attachment' not in cdispo:
								body = part.get_payload(decode=True)  # decode
								extracted_message = re.sub('(?<=[ @.a-zA-Z0-9])[\r][\n](?=[ @.a-zA-Z0-9])', ' ', body)
								print extracted_message
								break
					else:
						part = msg.get_payload()
						ctype = part.get_content_type()
						cdispo = str(part.get('Content-Disposition'))
						# skip any text/plain (txt) attachments
						if ctype == 'text/plain' and 'attachment' not in cdispo:
							body = part.get_payload(decode=True)  # decode
							extracted_message = re.sub('(?<=[ @.a-zA-Z0-9])[\r][\n](?=[ @.a-zA-Z0-9])', ' ', body)
							print extracted_message
							break

	except Exception, e:
		print str(e)

# read_email_from_gmail()