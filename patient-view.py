import datetime as dt
from urllib.parse import urlencode

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from thefuzz import fuzz
import requests
import os
import json
import argparse
import sys
from faker import Faker
from faker_healthcare import HealthcareProvider
import random
from datetime import date, datetime



def get_session():
	session = OAuth2Session(
        client_id=CLIENT_ID,
        client_secret=PRIVATE_KEY,
        scope=SCOPES,
        token_endpoint_auth_method=PrivateKeyJWT(
            token_endpoint=TOKEN_ENDPOINT,
            alg="RS384",
        ),
    )
    	
	return session
	
	
def get_token(session):
	token = session.fetch_token(TOKEN_ENDPOINT, verify=VERIFY)
	return token
	


def view_all_patients(session):
	response = session.get(f"{FHIR_URL}/Patient", verify=VERIFY)
	return response


def view_patient(session, puuid):
	response = session.get(f"{FHIR_URL}/Patient/{puuid}", verify=VERIFY)
	return response
	
	

def add_patient(session, family_name="Doe", given_name="John"):
	payload = {
	"resourceType": "Patient",
	"name": [
	{
	  "use": "official",
	  "family": f"{family_name}",
	  "given": [f"{given_name}"]
	}
	],
	"gender": "female",
	"birthDate": "1990-05-15",
	"active": True,
	"deceasedBoolean": False,
	}

	

	#add a patient
	response = session.post(f"{FHIR_URL}/Patient", verify=False, json=payload)

	#print(response)
	#print(response.json())

	#Get PUUID from response
	#puuid = get_puuid(response.json())
	
	return response
	


def add_fake_patient(session):
	fake = Faker("en_US") #use locale, for phone numbers and such
	
	
	bit = random.randint(0, 1)
	if bit == 0:
		gender = "male"
		given_name = fake.first_name_male()
	else:
		gender = "female"
		given_name = fake.first_name_female()
	
	#gender = "male"
	family_name = fake.last_name()
	#given_name = "Mike"
	birthDate = fake.date_between(start_date='-95y', end_date='today')
	deceasedBoolean = "false"  
	home_street_address = fake.street_address().upper()
	city = fake.city().upper()
	state = fake.state_abbr().upper()
	postal_code = fake.zipcode()
	country = "USA".upper()
	home_phone = ''
	mobile_phone = fake.bothify(text='(###) ###-####')
	ssn = fake.ssn()
	
	payload = {
	"resourceType": "Patient",
	"identifier": [
		{
		"type": {
			"coding": [
				{
				"code": "SS",
				}
			]
			},
		"value": f"{ssn}",
	}
	],
	"name": [
	{
	  "use": "official",
	  "family": f"{family_name}",
	  "given": [f"{given_name}"]
	}
	],
	"gender": f"{gender}",
	"birthDate": f"{birthDate}",
	"active": True,
	"deceasedBoolean": f"{deceasedBoolean}",
	
	"telecom": [
	{
		"system": "phone",
		"value": f"{mobile_phone}",
		"use": "home",
	},
	],
	 "address": [
    {
      "use": "home",
      "type": "both",
      "line": [
        f"{home_street_address}"
      ],
      "city": f"{city}",
      "state": "MD",
      "postalCode": f"{postal_code}",
      "country": f"{country}",
      "period": {
        "start": "2026-11-06T15:58:48.000-05:00"
      }
    }
    ]
    }
  
	
	#add a patient
	response = session.post(f"{FHIR_URL}/Patient", verify=False, json=payload)
	
	print(response.status_code)
	print(response.json())

	
	return response
	
	
	

def view_conditions(access_token):
	#response = session.get(f"{FHIR_URL}/Condition", verify=VERIFY)
	
	headers = {
	    'Authorization': f'Bearer {access_token}',
	    'Content-Type': 'application/fhir+json',
	    'Accept': 'application/fhir+json',
	}
	
	
	condition_payload = {
	    'resourceType': 'Condition',
	    'clinicalStatus': {
		'coding': [
		    {
		        'system': 'http://hl7.org',
		        'code': 'active',
		    }
		]
	    },
	    'verificationStatus': {
		'coding': [
		    {
		        'system': 'http://hl7.org',
		        'code': 'confirmed',
		    }
		]
	    },
	    'subject': {'reference': f'Patient/a32750e0-4497-4b90-beb4-cc82d72e8597'},
	    'onsetDateTime': '2026-01-15',
	}
	
	response = session.get(f"{FHIR_URL}/Condition", verify=VERIFY, data=json.dumps(condition_payload))
	
	return response


	
def view_condition(access_token, patient_uuid):
	#print(f"View Condition for {patient_uuid}")
	
	headers = {
	    'Authorization': f'Bearer {access_token}',
	    'Accept': 'application/fhir+json',
	}
	
	
	
	response = session.get(f"{FHIR_URL}/Condition?patient={patient_uuid}", verify=VERIFY)
	
	if response.ok:
		'''
		print(response)
		print(f"VIEW CONDITION: {json.dumps(response.json())} \n")
		print(f"{response.json()["entry"][0]["resource"]["code"]["text"] }")
		print(f"{response.json()["entry"][0]["resource"]["note"][0]["text"] }")
		'''
		
		conditions = {}
		
		entry_list = response.json()["entry"]
		
		for i, item in enumerate(entry_list):
			#print(f"{i} : {item["resource"]["code"]["text"]}")
			conditions[item["resource"]["code"]["text"]] = []
			
			temp_notes_list = []
			if "note" in response.json()["entry"][i]["resource"]:
				#print(f"There are notes for {item}")
				note_list = response.json()["entry"][i]["resource"]["note"]
				for j, note in enumerate(note_list):
					#print(f"{j} : {note_list[j]["text"]}")
					temp_notes_list.append(note_list[j]["text"])
				conditions[item["resource"]["code"]["text"]] = temp_notes_list	
				#print('\n')
					
			
			
		#print(f"CONDITIONS: {conditions} ")
	
		return response, conditions
	else:
		return 0
	
		
	
def add_condition(access_token, patient_uuid, condition="Hypertension", given_date=None):
	print(f"Adding condition {condition}  to  patient {patient_uuid}")
	
	if given_date is None:
		given_date = date.today()
		
	print(f"Given Date:  {given_date}")
	
	# 2. Set up the authorization headers
	headers = {
	    'Authorization': f'Bearer {access_token}',
	    'Content-Type': 'application/fhir+json',
	    'Accept': 'application/fhir+json',
	}

	# 3. Build the FHIR Condition payload
	# Replace 'Patient/123' with the actual patient reference ID in your system
	condition_payload = {
	    'resourceType': 'Condition',
	    'clinicalStatus': {
		'coding': [
		    {
		        'system': 'http://hl7.org',
		        'code': 'active',
		    }
		]
	    },
	    'verificationStatus': {
		'coding': [
		    {
		        'system': 'http://hl7.org',
		        'code': 'confirmed',
		    }
		]
	    },
	    'code': {
		'coding': [
		    {
		        'system': 'http://snomed.info',
		        'code': '38341003',
		        'display': 'Hypertensive disorder',
		    }
		],
		'text': 'Hypertension',
	    },
	    'subject': {'reference': f'Patient/{patient_uuid}'},
	    'onsetDateTime': '2026-01-15',
	}
	
	condition_payload = {
	    'resourceType': 'Condition',
	    'verificationStatus': {
		'coding': [
		    {
		        'system': 'http://hl7.org',
		        'code': 'confirmed',
		    }
		]
	    },
	    'code': {
		'coding': [
		    {
		        'system': 'http://snomed.info',
		        'code': '38341003',
		        'display': f'{condition}',
		    }
		],
		'text': f'{condition}',
	    },
	    'subject': {'reference': f'Patient/{patient_uuid}'},
	    'onsetDateTime': f'{given_date}',
	}

	# 4. Make the POST request
	'''
	response = requests.post(
	    f'{FHIR_URL}/Condition', headers=headers, verify=False, data=json.dumps(condition_payload)
	)
	'''
	response = session.post(f"{FHIR_URL}/Condition", verify=VERIFY, data=json.dumps(condition_payload))

	# 5. Check the result
	if response.status_code == 201:
	    print('Condition created successfully!')
	    print(response.json())
	else:
	    print(
		f'Failed to create condition. Status Code: {response.status_code}'
	    )
	    print(response.text)

	
	return response
	

def get_puuid(json_response: dict, family_name=None, given_name=None):
	#print(f"get_puuid: {json_response}")
	entry_list = json_response["entry"]
	
	for item in entry_list:
		#print(f"ITEM: {json.dumps(item)}")
		#json.dumps(data, indent=4)
		puuid = item["resource"]["id"]
		
		if family_name is not None:
			found_family_name = item["resource"]["name"][0]["family"]
			found_given_name = item["resource"]["name"][0]["given"][0] #just the first given name
			print(f"FOUND FAMILY: {found_family_name} FOUND GIVEN: {found_given_name}")
			score = fuzz.ratio(str(family_name).lower(), str(found_family_name).lower())
			#print(f"SCORE = {score}")
			if score >= 95:
				#print(f"FOUND!")
				return puuid
		 
	#print(f"PUUID: {puuid}")	
	
	return puuid
	
	

if __name__ == "__main__":
	fake = Faker("en_US") #use locale, for phone numbers and such
	fake.add_provider(HealthcareProvider)
	
	print("Trying....")

	# Force all downstream requests/authlib sessions to skip SSL verification
	os.environ['CURL_CA_BUNDLE'] = ''
	VERIFY = False # False means do NOT verify certificates - used in testing with self-signed certificates.

	BASE_URL = "https://localhost"
	OAUTH_URL = BASE_URL + "/oauth2/default"
	FHIR_URL = BASE_URL + "/apis/default/fhir"
	API_URL = BASE_URL + "/api/patient"
	TOKEN_ENDPOINT = f"{OAUTH_URL}/token"

    
	#CLIENT_ID = "fh0w0PPlsgxVaRfEvM9wV_Ek21syTO3N04LnLH_9Tz8" #App 8
	#CLIENT_ID = "9_cdSZI8YsvngcFCkgDaO2yQ-rRal40mFCnAhaiGjGk" #App 9
	CLIENT_ID = "dV2uWltyarCFLn3xcqYpfXau5rK5p90h00NC3Uoi9co" #App 10
	CLIENT_ID = "ZgXpUg3Pk6dXTlnVT5T32nsiTDNihHJVuw6__5_-xVY" #App 11
    
	SCOPES = [
        "system/Condition.c system/Condition.r system/Condition.s user/Patient.read system/Patient.write system/Patient.s system/Patient.r",
    ]
     
    

	PRIVATE_KEY = "..."
    
    
    
	# 1. Initialize the parser
	parser = argparse.ArgumentParser(description="A script to process patients in Open-EMR.")

	# 2. Add positional arguments (Required by default)
	#parser.add_argument("view", type=str, help="View patient (all if no options are given)")

	parser.add_argument("-m", "--mode", choices=['view', 'add', 'delete'], required=True, help="What to do.")

	# 3. Add optional arguments/flags (Starts with dashes)
	parser.add_argument("-f", "--fake", type=str, nargs='?', const=1, default="",  help="Generate fake entry.")  #number of args (0,1)
	parser.add_argument("--number", type=str, nargs='?', const=1, default=1,  help="Number of fake entries.")  
	parser.add_argument("-p", "--patient", type=str, nargs='?', const=1, default="",  help="A patient.")  #number of args (0,1)
	parser.add_argument("-c", "--condition", type=str, nargs='?', const=1, default="", help="A new medical condition.")
	parser.add_argument("-n", "--name", type=str, help="A patient name. (Last, First)")
	parser.add_argument("-u", "--uuid", type=str, help="A patient UUID.")
	

	# 4. Parse the terminal arguments
	args = parser.parse_args()

	
	# Load your private key
	with open('private.key', 'r') as f:
		PRIVATE_KEY = f.read()
		    
	# Load your public key
	#with open('public.pem', 'r') as f:
	#    PUBLIC_KEY = f.read()
		
	session = get_session()

	token= get_token(session)


	print(f"TOKEN: {token}")

	# Create 2 fake patients
	#uv run patient-view.py -m add -f -p --number 2
		
	if args.mode == "view":
		if args.name:
			#lookup by name
			# first have to get a list of all patients
			response = view_all_patients(session)
			if response.ok:
				#Get PUUID from response from view_all_patients for a name
				last_name, first_name = [item.strip() for item in args.name.split(",")]
				puuid = get_puuid(response.json(), last_name, first_name)
				
				print(f"PUUID: {puuid} for {last_name}, {first_name}")
				
				response = view_patient(session, puuid)
				print(f"Patient: {json.dumps(response.json())} ")
				
				
				response, conditions = view_condition(token, puuid)
				#print(f"Patient: {response.json()}")
				print(f"Patient: {json.dumps(response.json())} ")
				print(f"Conditions: {conditions}")
		
		elif args.uuid:
			#lookup by uuid
			puuid = args.uuid
			response = view_patient(session, puuid)
			#print(response)
			if response.ok:
				print(response.json())
		
		elif args.condition:
			if args.condition == "":
				#view all conditions
				response = view_conditions(token)
				#print(response)
				if response.ok:
					print(response.json())
			else:
				#view one condition
				pass
		else:
			#view all patients
			response = view_all_patients(session)
			#print(response)
			if response.ok:
				print(response.json())

	elif args.mode == "add":
		print(f"Adding....")
		if args.patient:
			#add a new patient
			print(f"Adding a patient {args.patient}....")
			if (not args.name) or (args.name == "") and (args.fake):
				#add a fake random patient
				print(f"Adding {args.number} fake random patient(s): {args.name}")
				for i in range(int(args.number)):
					#create a fake patient
					print(f"Adding fake patient# {i}")
					response = add_fake_patient(session)
					puuid = response.json()['uuid']
					print(f"Adding fake condition for patient[{i}]")
					
					random_number = random.randint(1, 3)
					for i in range(random_number):
						result = add_condition(token, puuid, fake.disease())
					
				pass
			else:
				#add a provided name
				print(f"Adding a provided name: {args.name}")
				last_name, first_name = [item.strip() for item in args.name.split(",")]
				response = add_patient(session, last_name, first_name)
				#print(response)
				if response.ok:
					print(response.json())
				
		elif (not args.condition) or (args.condition == ""):
			#add a new medical condition
			if args.name:
				#add a provided condition
				pass
			else:
				#add a random conditon
				pass

	sys.exit()
	
	payload = {
	"resourceType": "Patient",
	"name": [
	{
	  "use": "official",
	  "family": "Doe",
	  "given": ["Jane"]
	}
	],
	"gender": "female",
	"birthDate": "1990-05-15",
	"active": True,

	}

	

	#add a patient
	#response = session.post(f"{FHIR_URL}/Patient", verify=False, json=payload)

	#print(response)
	#print(response.json())

	#Get PUUID from response
	#puuid = get_puuid(response.json())
	
	

	#Get PUUID from response from view_all_patients for a name
	puuid = get_puuid(response.json(), "Stone", "Michael")

	print(f"PUUID: {puuid}")

	# vew all conditions
	response = view_conditions(token)
	print(response)
	print(response.json())

	'''
	#Add condition for a patient with a given puuid
	puuid = 'a3197524-f916-47ad-ad0c-66f8c4b9fe87'
	result = add_condition(token, puuid, "hypertension")
	'''
