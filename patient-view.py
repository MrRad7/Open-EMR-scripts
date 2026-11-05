import datetime as dt
from urllib.parse import urlencode

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from thefuzz import fuzz
import requests
import os
import json



def get_session():
	print(f"SCOPES: {SCOPES}")
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
	token = session.fetch_token(TOKEN_ENDPOINT, verify=False)
	return token
	


def view_all_patients(session):
	response = session.get(f"{FHIR_URL}/Patient", verify=False)
	return response


def view_patient(session, puuid):
	response = session.get(f"{FHIR_URL}/Patient/{puuid}", verify=False)
	return response
	
	

def view_conditions(access_token):
	#response = session.get(f"{FHIR_URL}/Condition", verify=False)
	
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
	    'subject': {'reference': f'Patient/a32750e0-4497-4b90-beb4-cc82d72e8597'},
	    'onsetDateTime': '2026-01-15',
	}
	
	response = session.get(f"{FHIR_URL}/Condition", verify=False, data=json.dumps(condition_payload))
	
	return response
	
def view_condition(access_token, patient_uuid):
	response = session.get(f"{FHIR_URL}/Condition/{puuid}", verify=False)
	return response
	
	
	
	
		
	
def add_condition(access_token, patient_uuid, condition="Hypertension" ):
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

	# 4. Make the POST request
	'''
	response = requests.post(
	    f'{FHIR_URL}/Condition', headers=headers, verify=False, data=json.dumps(condition_payload)
	)
	'''
	response = session.post(f"{FHIR_URL}/Condition", verify=False, data=json.dumps(condition_payload))

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
	print(f"get_puuid: {json_response}")
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
    print("Trying....")

    # Force all downstream requests/authlib sessions to skip SSL verification
    os.environ['CURL_CA_BUNDLE'] = ''

    BASE_URL = "https://localhost"
    OAUTH_URL = BASE_URL + "/oauth2/default"
    FHIR_URL = BASE_URL + "/apis/default/fhir"
    API_URL = BASE_URL + "/api/patient"
    TOKEN_ENDPOINT = f"{OAUTH_URL}/token"

    CLIENT_ID = "_T2D4MMKxL63i8k0wSqxXfzzpycWl5p9HXHMNubE77Q" #new
    #CLIENT_ID = "8B8y5qLX6me1vkxR8AZQp-GDgi2Bp6180xgkeF8PXj8" #original
    CLIENT_ID = "ip3ZgRpL4HMOuD-yaMmOH66Nip4DAsy-u7YvhyZbsMg" #App4
    CLIENT_ID = "rMaUQHZEUKhlrzto1Aipv8jHeICY_GTxK1LiH1mtY4Y"
    CLIENT_ID = "Se7ZaR5VkkoF0kq3M7afZh9xSm3hq2YWd-Mu7vfDr7M" #App 5
    CLIENT_ID = "vpYzk-dOKn4GSmg2sNS8T0QG6Jkmc_zXOvkgsc_uICg" #App 6
    CLIENT_ID = "yZG0qO_ugWynI0K2AwQpeVqmDZkOZFNxKR58T9Fw_Tg" #App 7
    CLIENT_ID = "fh0w0PPlsgxVaRfEvM9wV_Ek21syTO3N04LnLH_9Tz8" #App 8
    CLIENT_ID = "vCB02n95SAcj2hZ_eWhXlNlaFoQ82gWv-TUD2oEZWhk" #App 9
    
    SCOPES = [
        "system/Condition.c system/Condition.r system/Condition.s user/Patient.read system/Patient.write system/Patient.s",
    ]
    #patient/Condition.write 

    PRIVATE_KEY = "..."

    # Load your private key
    with open('private.key', 'r') as f:
        PRIVATE_KEY = f.read()
            
    # Load your public key
    #with open('public.pem', 'r') as f:
    #    PUBLIC_KEY = f.read()
        
    session = get_session()
    
    token= get_token(session)


    print(f"TOKEN: {token}")
    
    
    
    
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

    
    response = view_all_patients(session)
    print(response)
    print(response.json())
    
    
    #response = session.post(f"{FHIR_URL}/Patient", verify=False, json=payload)
    
    #print(response)
    #print(response.json())
    
    #Get PUUID from response
    #puuid = get_puuid(response.json())
    
    #Get PUUID from response from view_all_patients for a name
    puuid = get_puuid(response.json(), "Stone", "Michael")
    
    print(f"PUUID: {puuid}")
    
    response = view_conditions(token)
    print(response)
    print(response.json())
    
    '''
    puuid = 'a3197524-f916-47ad-ad0c-66f8c4b9fe87'
    result = add_condition(token, puuid, "hypertension")
    '''
