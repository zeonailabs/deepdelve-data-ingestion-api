import os
DB_HOST = os.getenv("RDS_HOSTNAME", "deepdelvedb.cprtnh47zla5.us-east-1.rds.amazonaws.com")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "deepdelve_survey_store")
DB_USERNAME = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Deepdelve#123")

SQLALCHEMY_DATABASE_URI =  "mysql+mysqlconnector://"+DB_USERNAME+":"+DB_PASSWORD+"@"+DB_HOST+":"+DB_PORT+"/"+DB_NAME