import requests

headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtZXJyZW4iLCJleHAiOjE2ODkzNDQ0NDd9.8nOQzpUrht24rT0fFUdI0HYs220pDpznBjRfvjQF-Gk',
    'Content-Type': 'application/json',
}

json_data = {
    'surveyList': [
        {
            'surveyId': 'string1',
        },
    ],
}

response = requests.post(
    'https://4v2xpknbhwnywsxk4qnnoje7di0onlzf.lambda-url.us-east-1.on.aws/v1/deepdelve/survey/delete',
    headers=headers,
    json=json_data,
)
if response.status_code == 200:
    print("Survey Data deletion successful. Status code:", response.status_code, "response :",response.text)
else:
    print("Survey Data deletion failed. Status code:", response.status_code, "response :", response.text)