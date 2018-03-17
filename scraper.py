import seleniumqueue
from lxml import html
import time
import datafetcher
from diskcache import Cache

#Required for running selenium on server

attendance_cache = Cache('/tmp/mycachedir/attendance')
marks_cache = Cache('/tmp/mycachedir/marks')

def scrape(registration_number,password,action,args=False):
	try:
		if action is 'check_registration':
			message = check_registration(registration_number,password)
		if action is 'attendance':
			message = get_attendance(registration_number,password,args)
		if action is 'marks':
			message = get_marks(registration_number,password,args)
		if action is 'timetable':
			message = get_timetable(registration_number,password,args)
	except TimeoutException:
		message = "Page failed to load. Please try again"
	return message

def get_attendance(registration_number,password,args):
	if (attendance_cache.get(registration_number) is None):
		html = seleniumqueue.get_source("http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=7")
		attendance_cache.set(registration_number,html,expire=30)
		browser.quit()
	else:
		html = attendance_cache.get(registration_number)
	if not args:
		message = datafetcher.scrape_attendance_all(html)
	else:
		message = datafetcher.scrape_attendance_subject(html," ".join(args))
	return message

def get_marks(registration_number,password,args):
	if (marks_cache.get(registration_number) is None):
		html = seleniumqueue.get_source("http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=16")
		message = datafetcher.scrape_marks_all(html)
		marks_cache.set(registration_number,message,expire=120)
	else:
		message = marks_cache.get(registration_number)
	return message

def get_timetable(registration_number,password,args):
	html = seleniumqueue.get_source(registration_number,password,"http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=5")
	message = datafetcher.scrape_timetable_all(html)
	return message

def check_registration(registration_number,password):
	html = seleniumqueue.get_source(registration_number,password,"http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=1")
	if "Father Name" not in html:
		raise AssertionError()
	name = datafetcher.validate_registration(html)
	return name
