# [X] made regular http requests
# [ ] Checks to see if selenium is needed
# [ ] Runs in selenium with all the information already gathered
# [ ] Runs a through a proxy if desired.
# [ ] Dynamically (big word :O) checks and changes the headers for the GET/POST
# [ ] check for recaptcha and csrf tokens.
# [ ] Get the form daya to be accessible for selenium as well :3

import requests
import sys
import time
import random
from faker import Faker
from bs4 import BeautifulSoup

#global declarations
fake = Faker()


#code to get the information from the page.
def FORM_GRAB(link, proxies):
	#form a session, then get the response
	session = requests.Session()
	
	

	# Send the GET request to retrieve the form with dynamic headers
	response = session.get(link)
	
	
	#check if site could be reached
	if 300 <= response.status_code < 400:
		print("Redirect response code given.")
		new_url = response.headers.get('Location')
		
		if new_url:
			print("New location is at: " + new_url)
			print("Try new site? (Put \"YES\" for yes)")
			answer = input()
			if answer == "YES":
				url = new_url
				FORM_GRAB(url)
				return True
			else:
				return False
		
		print("no redirect link given")
		return False
		
	elif response.status_code != 200:
		print("unable to reach site. Response code: " + str(response.status_code))
		return False
	
	#check for the user input fields
	soup = BeautifulSoup(response.text, "html.parser")
	input_form = soup.find('form') #took me much longer than i would like to admit to realize where this is searching -_-
	if input_form is None:
		print("no input form found on the page.")
		return False
	
	#get the URL for submission
	submit_URL = input_form.get("action")
	if not submit_URL.startswith("http"): #if it doesn't start with http, then it's referencign a site within it'self and needs to add it onto the url :3
		submit_URL = link + submit_URL
		#print(submit_URL)
	#setting up the submission data :D
	form_data = {}	
	
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
				
	
	if proxies:
		response = session.post(submit_URL,data=form_data,proxies=proxies)
	else:
		response = session.post(submit_URL,data=form_data)
	
	
	if response.status_code == 200:
		print(f"Form successfully submitted to {submit_URL}")
		session.cookies.clear_session_cookies()
		session.close()
	else:
		print(f"Failed to submit form. Status code: {response.status_code}")
		session.cookies.clear_session_cookies()
		session.close()
		return False


	#make it check for a captcha or csrf token to see if selenium is needed, then switch to selenium with all the information gathered

#main loop
def main():
	url = "<insert URL>
	#proxieThings = {"http" : "socks5h://127.0.0.1:9150", "https" : "socks5h://127.0.0.1:9150"}
	proxieThings = False
	code_run = True
	while code_run:
		http_run = FORM_GRAB(url, proxieThings)
		if http_run:
			continue
		else:
			#put selenium here
			code_run = http_run
		
		
if __name__ == "__main__":
	main()

