import Queue
import time
import selenium
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

#Required to running selenium on server
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 600))
display.start()


q = Queue.Queue(4)
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
timeout = 3

def get_source(reg_num,pwd,url):
	browser = q.get()

	try:
	        element_present = EC.presence_of_element_located((By.ID, 'txtRegNumber'))
	        WebDriverWait(browser, timeout).until(element_present)
        except TimeoutException:
	        print "Timed out waiting for page to load"
		add_to_queue(browser)
		raise TimeoutException
	registration_number_element = browser.find_element_by_name("txtRegNumber")
	password_element = browser.find_element_by_id("txtPwd")
	registration_number_element.send_keys(reg_num)
        password_element.send_keys(pwd)
	images = browser.find_elements_by_tag_name('img')
	time.sleep(1)
        images[0].click()
	browser.get(url)
	source = browser.page_source 
	add_to_queue(browser)
	return source

def add_to_queue(browser):
	browser.delete_all_cookies()
	browser.get("http://evarsity.srmuniv.ac.in/srmswi/usermanager/ParentLogin.jsp")
	q.put(browser)


print q.qsize()
for i in range(0,4):
	browser = webdriver.Chrome("drivers/chromedriver",chrome_options=options)
	add_to_queue(browser)
