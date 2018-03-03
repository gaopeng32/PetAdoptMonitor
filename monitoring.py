# Written by Peng Gao (gaopeng32@gmail.com) in March 2018

import os
import re
import urllib.request
from bs4 import BeautifulSoup
import time
import smtplib

from email.mime.text import MIMEText


pet_words = ["犬", "狗"]
adopt_words = ["领", "收"]
#breed_words = ["阿拉斯加"]


def check_match(str):
	for pet in pet_words:
		for adopt in adopt_words:
			if pet in str and adopt in str:
				return True

def send_email(fromaddr, toaddrs, info):
	# Create the email message
	msg = MIMEText(info, 'html')
	msg['Subject'] = 'Find a new pet!'
	msg['From'] = fromaddr
	msg['To'] = ', '.join(toaddrs)

	# Setup the e-mail server and send e-mail
	try:
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login("gaopeng32@gmail.com", "password")
		server.sendmail(fromaddr, toaddrs, msg.as_string())
		server.quit()
	except:
		print('Something went wrong...')


def main():
	"""
		Monitor website www.moonbbs.com for new pet adopt information. 
		Send e-mail when new information is added.
	"""

	first_match_div_on_record = None

	while True:
		if first_match_div_on_record is None:
			print('No record')
		else:
			print('Current top item%s' % first_match_div_on_record.get_text())

		# Configure url sorted by post time
		url = 'http://www.moonbbs.com/forum.php?mod=forumdisplay&fid=61&filter=author&orderby=dateline&typeid=214&forumdefstyle=yes'
		
		# Get HTML page
		response = urllib.request.urlopen(url)
		soup = BeautifulSoup(response.read(), "html5lib")

		# Monitor if the first matched item changes
		divs = soup.find_all('tbody', id=re.compile('^normalthread_'))
		first_match_div = None
		for div in divs:
			first_match_div = div.find('a', class_="xst")
			title_str = first_match_div.get_text()
			if check_match(title_str):
				break

		if first_match_div_on_record is None and first_match_div is not None:
			# Initialization record
			print('Initialize record')
			first_match_div_on_record = first_match_div

		if (first_match_div_on_record is not None 
			and first_match_div is not None 
			and first_match_div != first_match_div_on_record):
			print('Send e-mail and update record')

			# Extract the new item as html string
			link = first_match_div.get('href')
			text = first_match_div.get_text()
			info = u'<a href="%s">%s</a>' % (link, text)

			# Send e-mail
			send_email('gaopeng32@gmail.com', ['pgao@princeton.edu'], info)

			# Update record
			first_match_div_on_record = first_match_div
		else:
			print('No new item. Wait.')

			# Wait for 60 minutes
			time.sleep(3600)

			# Continue monitoring
			continue




if __name__ == "__main__":
    main()


