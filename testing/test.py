from rest_api.controller.utils import delete_folder_from_s3
test = delete_folder_from_s3("survey_data/1001/string/")
print(test)