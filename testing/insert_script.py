import requests
import csv
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtZXJyZW4iLCJleHAiOjE2ODkzNDQ0NDd9.8nOQzpUrht24rT0fFUdI0HYs220pDpznBjRfvjQF-Gk',
    'Content-Type': 'application/json',
}

def make_survey_data(csvFilePath):
	
	# create a dictionary
	data_list = []
	
	# Open a csv reader called DictReader
	with open(csvFilePath, encoding='utf-8') as csvf:
		csvReader = csv.DictReader(csvf)
		
		# Convert each row into a dictionary
		# and add it to data
		i=1
		for rows in csvReader:
			data = {}
			# Assuming a column named 'No' to
			# be the primary key
			data["Id"] = str(i)
			d_data = []
			for k,v in rows.items():
				d = {}
				d["key"] = k
				d["value"] = v
				d_data.append(d)
			data["Data"]= d_data
			i+=1
			data_list.append(data)
	return data_list

csvFilePath = r'/home/biswa/Documents/GitHub/deepdelve-data-ingestion-api/merren_survey - Sheet1.csv'

data_list = make_survey_data(csvFilePath= csvFilePath)
json_data = {
    'surveyList': [
        {
            'surveyId': 'new',
            'metaData': [
                {
                    'metaKey': 'string',
                    'value': 'string',
                },
            ],
            'surveyDescription': 'string',
            'surveyData': data_list,
        },
    ],
}

insert_response = requests.post(
    'https://4v2xpknbhwnywsxk4qnnoje7di0onlzf.lambda-url.us-east-1.on.aws/v1/deepdelve/survey/insert',
    headers=headers,
    json=json_data,
)
# print(insert_response.text)
if insert_response.status_code == 200:
    print("Survey Data insertion successful. Status code:", insert_response.status_code, "response :", insert_response.text)
else:
    print("Survey Data insertion failed. Status code:", insert_response.status_code, "response :", insert_response.text)
