# [X] made regular http requests
# [~] Checks to see if selenium is needed
#	-Doesn't really check, more just assumes if requests doesn't work.
# [~] Runs in selenium with all the information already gathered
#	[~] Runs - kinda? it will do it, just easily detected...
#	[ ] Driver runs in background
# [~] Runs a through a proxy if desired.
#	[X] Requests Proxy
#	[ ] Webdriver Proxy
# [ ] Dynamically (big word :O) checks and changes the headers for the GET/POST
# [ ] check for recaptcha and csrf tokens.
# [X] Get the form daya to be accessible for selenium as well :3

import requests
import sys
import time
import random
from faker import Faker
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

#global declarations
fake = Faker()
form_data = {}
url_index = 1#using this to check if we need to do another form data grab


def _cookies_grabber():
	print("to be filled in")

#to get the header info
def _headers_grabber():
	print("to be filled in")

#to grab the page info for requests
def _form_grab(input_form):
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
def _driver_session(driver,link, proxies):
	
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
			field.send_keys(fake.paragraph(nb_sentences=random.randint(3, 10)))
		
		elif fieldType == "text":# and fieldName:
			if "first_name" in fieldName or "first-name" in fieldName:
				field.send_keys(fake.first_name())
			elif "last_name" in fieldName or "last-name" in fieldName:
				field.send_keys(fake.last_name())
			elif "name" in fieldName or "full-name" in fieldName or "full_name" in fieldName:
				field.send_keys(fake.name())
			elif "location" in fieldName:
				field.send_keys(fake.address())
			elif "zipcode" in fieldName:
				field.send_keys(str(random.randint(10000, 99999)))
			else:
				field.send_keys(fake.paragraph(nb_sentences=random.randint(3,10)))
		elif fieldType == "email":
			field.send_keys(fake.email())

		elif fieldType == "number":
			field.send_keys(fake.phone_number())

		elif fieldType == "radio":
			# Group radio buttons by name
			if fieldName in radio_groups:
				radio_groups[fieldName].append(field)
			else:
				radio_groups[fieldName] = [field]

		elif fieldType == "checkbox":
			# Randomly check/uncheck the checkbox
			if random.choice([True, False]):
				field.click()
				
		elif fieldTag == 'textarea':
			form_data[field_Name] = fake.paragraph(nb_sentences=50)

	# Randomly selecting and clicking one radio button from each group
	for radio_group in radio_groups.values():
		random.choice(radio_group).click()

	try:
		submit_button = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Submit') or contains(text(), 'Sign Up')]")
		driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
		time.sleep(1.5)
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
	if "success" in driver.current_url or "thank-you" in driver.current_url:
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
	
	_form_grab(input_form)
	
	
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
	url = [<Put URLS HERE IN THIS LIST =>:3>]
	#proxieThings = {"http" : "socks5h://127.0.0.1:9150", "https" : "socks5h://127.0.0.1:9150"}
	proxieThings = False
	code_run = True
	
	for x in url:
		#request attempts
		requests_run = True
		while requests_run:
			requests_run = _request_session(x, proxieThings)
			if requests_run:
				waitTime = (str(random.randint(0,5))+"."+str(random.randint(0,9)))
				print("Requests Waiting " + waitTime + " seconds")
				time.sleep(float(waitTime))
				#continue
			else:
				print(f"Requests stop for {x}")
		
		#driver attempts
		driver_run = True
		#putting webdriver here so it'll be a persistant session.
		firefox_options = Options()
		firefox_options.headless = True  # Optional: run without opening the browser
		firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

		driver = webdriver.Firefox(options=firefox_options)
		while driver_run:
			driver_run = _driver_session(driver,x, proxieThings)
			time.sleep(0.5)
			if driver_run:
				waitTime = (str(random.randint(0,5))+"."+str(random.randint(0,9)))
				print(f"Driver Waiting {waitTime} seconds")
				time.sleep(float(waitTime))
			else:
				print(f"Driver stop for {x}")
				driver.quit()
				
		print(f"End of submissions for {x}")
		
if __name__ == "__main__":
	main()

