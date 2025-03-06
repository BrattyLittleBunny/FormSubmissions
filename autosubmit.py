'''
[X] made regular http requests
[~] Checks to see if selenium is needed
	-Doesn't really check, more just assumes if requests doesn't work.
[X] Runs in selenium with all the information already gathered
	[X] Runs
	[F] Driver runs in background - doesn't work D:
[X] Runs a through a proxy if desired.
	[X] Requests Proxy
	[X] Webdriver Proxy
[ ] Dynamically (big word :O) checks and changes the headers for the GET/POST
[~] check for recaptcha and csrf tokens.
	[X] Checks for csrf token
	[ ] Checks for recaptcha
'''
import requests
import sys
import time
import random
from faker import Faker
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

#global declarations
fake = Faker()
form_data = {}

#slowly types to make it seem more human
def slow_type(element, text):
	"""
	Type text slowly with a small delay between characters
	Adds realism and visibility to typing process
	stolen from arachnidInner. is a good idea :3
	"""
	for char in text:
		element.send_keys(char)
		time.sleep(random.uniform(0.09, 0.19))


def _cookies_grabber():
	print("to be filled in")

#to get the header info
def _headers_grabber():
	print("to be filled in")

#to grab the page info for requests
#original plan was to have this for both the driver and requests, but can't figure out how to do it XP
def _requests_form_grab(input_form):
	#check for the user input fields
	#setting up the submission data :D
	global form_data	
	
	for input_field in input_form.find_all(["input", "textarea", "select"]):
		input_type = input_field.get("type")
		field_Name = input_field.get("name")
		
		if field_Name:
			if input_type == "text":
				if "first_name" in field_Name or "first-name" in field_Name:
					form_data[field_Name] = fake.first_name()
				elif "last_name" in field_Name or "last-name" in field_Name:
					form_data[field_Name] = fake.last_name()
				elif "name" in field_Name or "full-name" in field_Name or "full_name" in field_Name:
					form_data[field_Name] = fake.name()
				elif "location" in field_Name:
					form_data[field_Name] = fake.address()
				elif "zipcode" in field_Name:
					form_data[field_Name] = str(random.randint(10000, 99999))
				else:
					form_data[field_Name] = fake.paragraph(nb_sentences=50)
			elif input_type == "email":
				form_data[field_Name] = fake.email()
			
			elif input_type == "number":
				form_data[field_Name] = fake.phone_number()
			
			elif input_field.get('tag') == 'select':
				options = input_field.find_all('option')
				if options:
					random_option = random.choice(options)
					form_data[field_Name] = random_option.get('value')
			
			elif input_type in ["checkbox", "radio"]:
				related_inputs = input_form.find_all("input", {"type": input_type, "name": field_Name})
				if related_inputs:
					chosen_input = random.choice(related_inputs)
					form_data[field_Name] = chosen_input.get("value", "on")
			
			elif input_field.get('tag') == 'textarea':
				form_data[field_Name] = fake.paragraph(nb_sentences=50)
				
			elif input_type == "hidden": #added hidden so that if there is a hidden value that is needed it's grabbed 
				form_data[field_Name] = input_field.get('value')
				
	
#web driver
def _driver_session(driver,link):
	
	driver.get(link)
	driver.implicitly_wait(2)

	#grabbing all the input fields
	input_fields = driver.find_elements(By.XPATH, "//input[not(@aria-hidden='true') and not(@type='hidden') and not(ancestor::*[@aria-hidden='true'])] | //textarea[not(@aria-hidden='true') and not(ancestor::*[@aria-hidden='true'])]")

	radio_groups = {}

	for field in input_fields:
		fieldType = field.get_attribute("type")
		fieldName = field.get_attribute("name") or field.get_attribute("id")
		fieldTag = field.get_attribute("tag")
		
		if fieldName == "g-recaptcha-response":  
		# Skip reCAPTCHA field
			continue
		
		if field.tag_name == "textarea":  
			print("Typing random text for big area")
			slow_type(field, fake.paragraph(nb_sentences=random.randint(3, 10)))
		
		elif fieldType == "text":# and fieldName:
			if "first_name" in fieldName or "first-name" in fieldName:
				print("Typing first name")
				slow_type(field, fake.first_name())
			elif "last_name" in fieldName or "last-name" in fieldName:
				print("Typing last name")
				slow_type(field, fake.last_name())
			elif "name" in fieldName or "full-name" in fieldName or "full_name" in fieldName:
				print("Typing full name")
				slow_type(field, fake.name())
			elif "location" in fieldName:
				print("Typing locatioin")
				slow_type(field, fake.address())
			elif "zipcode" in fieldName:
				print("Typing ZipCode")
				slow_type(field, str(random.randint(10000, 99999)))
			else:
				print("Typing random text")
				slow_type(field, fake.paragraph(nb_sentences=random.randint(3,10)))
		elif fieldType == "email":
			print("Typing email")
			slow_type(field, fake.email())

		elif fieldType == "number":
			print("Typing phone number")
			slow_type(field, fake.phone_number())

		elif fieldType == "radio":
			# Group radio buttons by name
			if fieldName in radio_groups:
				radio_groups[fieldName].append(field)
			else:
				radio_groups[fieldName] = [field]

		elif fieldType == "checkbox":
			# Randomly check/uncheck the checkbox
			if random.choice([True, False]):
				print("Clicking Check Box")
				field.click()
				
		elif fieldTag == 'textarea':
			print("Typing LARGE paragraph name")
			slow_type(field, fake.paragraph(nb_sentences=50))

	# Randomly selecting and clicking one radio button from each group
	for radio_group in radio_groups.values():
		print("Clicking radio group")
		random.choice(radio_group).click()

	try:
		submit_button = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Submit') or contains(text(), 'Sign Up')]")
		driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
		time.sleep(1.5)
		print("Clicking submit")
		submit_button.click()
	except Exception as e:
		print(f"Submit button not found: {e}")
		return False

	driver.implicitly_wait(2)

	success_indicators = [
		"//div[contains(@class, 'success')]",  # Success message with class containing 'success'
		"//p[contains(text(), 'Thank you')]",  # Common "Thank you" message
		"//h1[contains(text(), 'Success')]",   # Success header
	]

	for xpath in success_indicators:
		try:
			if driver.find_element(By.XPATH, xpath).is_displayed():
				return True
		except:
			continue

	# Alternative check: If URL changes, assume success
	if "success" in driver.current_url or "thank-you" in driver.current_url or "thankyou" in driver.current_url:
		print("Driver success")
		return True
	
	print("driver failed")
	return False  # If none of the success indicators were found

				
#http request session
def _request_session(link, proxies):
	#form a session, then get the response
	session = requests.Session()
	
	# Send the GET request to retrieve the form with dynamic headers
	responseG = session.get(link)
	
	#check if site could be reached
	if 300 <= responseG.status_code < 400:
		print("Redirect response code given.")
		new_url = responseG.headers.get('Location')
		
		if new_url:
			print("New location is at: " + new_url)
			print("Try new site? (Put \"YES\" for yes)")
			answer = input()
			if answer == "YES":
				url = new_url
				newcheck = _request_session(url)
				return True
			else:
				return False
		
		print("no redirect link given")
		return False
		
	elif responseG.status_code != 200:
		print("unable to reach site. Response code: " + str(responseG.status_code))
		return False
	
	soup = BeautifulSoup(responseG.text, "html.parser")
	input_form = soup.find('form') #took me much longer than i would like to admit to realize where this is searching -_-
	if input_form is None:
		print("no input form found on the page.")
		return False
	
	#get the URL for submission
	submit_URL = input_form.get("action")
	if submit_URL == None: 
		#print("No new URL to be added")
		submit_URL = link
	elif not submit_URL.startswith("http"): #if it doesn't start with http, then it's referencign a site within it'self and needs to add it onto the url :3
		submit_URL = link #+ submit_URL
		#print(submit_URL)
	
	_requests_form_grab(input_form)
	
	
	if proxies:
		responseP = session.post(submit_URL,data=form_data,proxies=proxies)
	else:
		responseP = session.post(submit_URL,data=form_data)
	
	
	if responseP.status_code == 200:
		print(f"Form successfully submitted to {submit_URL}")
		soup = BeautifulSoup(responseP.text, "html.parser")
		
		if "error" in responseP.request.url[len(submit_URL)-1:]:
			print(f"Error in submission. submition was to {responseP.request.url} instead -1")
			session.cookies.clear_session_cookies()
			session.close()
			return False
		
		if (submit_URL + "/") != responseP.request.url:
			#need to add a check to see if you want to keep going
			print(f"Error in submission. submition was to {responseP.request.url} instead")
			session.cookies.clear_session_cookies()
			session.close()
			return False
		
		#with open("postFile.txt", 'a') as f:
			#print(str(soup), file=f)
			#print(str(responseP.request.url) + "\n\n", file=f)
			#print(str(responseP.request.body) + "\n\n", file=f)
			#print(str(responseP.request.headers) + "\n\n", file=f)
			
			
		session.cookies.clear_session_cookies()
		session.close()
		
		return True
	else:
		print(f"Failed to submit form. Status code: {responseP.status_code}")
		session.cookies.clear_session_cookies()
		session.close()
		return False

	

#main loop
def main(): 
	url = ["<put list of URLs you want"]
	#proxies for if you want them
	#proxieThings = {"http" : "socks5h://127.0.0.1:9150", "https" : "socks5h://127.0.0.1:9150"}
	proxieThings = False
	code_run = True
	
	for x in url:
		#request attempts
		requests_run = True
		counter = 1
		while requests_run:
			print(f"Requests submission #{counter} starting")
			requests_run = _request_session(x, proxieThings)
			if requests_run:
				waitTime = (str(random.randint(0,5))+"."+str(random.randint(0,9)))
				print(f"Request submmission #{counter} for {x} is successful")
				counter += 1
				print(f"Requests Waiting {waitTime} seconds")
				time.sleep(float(waitTime))
				#continue
			else:
				print(f"Requests stop for {x}")
				print(f"Submitted {counter} times.")
		
		#driver attempts
		driver_run = True
		#putting webdriver here so it'll be a persistant session.
		print("Setting up Driver options!")
		firefox_options = Options()
		firefox_options.add_argument("-profile") 
		firefox_options.add_argument("<Input non cache firefox profile here>")
		#firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
		#if you have proxies you wanna use, this will activate. just put them in the proxieThings part :3
		if proxieThings:
			print("setting up driver proxy :D")
			proxy = Proxy()
			proxy.proxy_type = ProxyType.MANUAL
			try:
				proxy.http_proxy = proxieThings["http"]  # Example: "192.168.1.100:8080"
			except:
				print("no http proxy found D:")
			try:
				proxy.ssl_proxy = proxieThings["ssl"]  # Example: "192.168.1.100:8080"
			except:
				print("no ssl proxy found D:")
			firefox_options.set_proxy(proxy)
		driver = webdriver.Firefox(options=firefox_options)
		print("Driver ready")
		counter = 1
		while driver_run:
			print(f"Driver submission #{counter} starting")
			driver_run = _driver_session(driver,x)
			time.sleep(0.5)
			if driver_run:
				print(f"Driver submission #{counter} for {x} was successful")
				counter +=1
				waitTime = (str(random.randint(0,9))+"."+str(random.randint(0,9)))
				print(f"Driver Waiting {waitTime} seconds")
				time.sleep(float(waitTime))
			else:
				print(f"Driver stop for {x}")
				print(f"submitted {counter} times")
				driver.quit()
				
		print(f"End of submissions for {x}")
		
if __name__ == "__main__":
	main()
