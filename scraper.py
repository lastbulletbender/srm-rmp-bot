from lxml import html
import time
import selenium
import os
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import datafetcher
from diskcache import Cache

#Required for running selenium on server
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()

attendance_cache = Cache('/tmp/mycachedir/attendance')
marks_cache = Cache('/tmp/mycachedir/marks')

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
timeout = 3

def go_to_homepage(registration_number,password):
	browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver",chrome_options=options)
  	browser.get("http://evarsity.srmuniv.ac.in/srmswi/usermanager/ParentLogin.jsp")
	try:
		assert "SRM" in browser.title
	except:
		browser.quit()
		raise TimeoutException
	try:
		element_present = EC.presence_of_element_located((By.ID, 'txtRegNumber'))
		WebDriverWait(browser, timeout).until(element_present)
        except TimeoutException:
		browser.quit()
		raise TimeoutException

        registration_number_element = browser.find_element_by_name("txtRegNumber")
        password_element = browser.find_element_by_id("txtPwd")
        images = browser.find_elements_by_tag_name('img')
        registration_number_element.send_keys(registration_number)
        password_element.send_keys(password)
        time.sleep(1)
        images[0].click()
	return browser

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
		browser = go_to_homepage(registration_number,password)
		browser.get("http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=7")
		html = browser.page_source
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
		browser = go_to_homepage(registration_number,password)
		browser.get("http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=16")
		html = browser.page_source
		browser.quit()
		message = datafetcher.scrape_marks_all(html)
		marks_cache.set(registration_number,message,expire=120)
	else:
		message = marks_cache.get(registration_number)
	return message

def get_timetable(registration_number,password,args):
	browser = go_to_homepage(registration_number,password)
	browser.get("http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=5")
	html = browser.page_source
	browser.quit()
	message = datafetcher.scrape_timetable_all(html)
	return message

def check_registration(registration_number,password):
	browser = go_to_homepage(registration_number,password)
	browser.get("http://evarsity.srmuniv.ac.in/srmswi/resource/StudentDetailsResources.jsp?resourceid=1")
	html = browser.page_source
	if "Father Name" not in html:
		browser.quit()
		raise AssertionError()
	name = datafetcher.validate_registration(html)
	browser.quit()
	return name
