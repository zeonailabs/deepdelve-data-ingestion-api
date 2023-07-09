import os

# AWS credential
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "AKIA55DPZLRNKNRCQIXZ")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "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")
AWS_REGION_VALUE = os.getenv("AWS_REGION_VALUE", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "deepdelveclientdata")


# READER_CONFIG
SEARCH_TARGET_PLATFORM = os.getenv("SEARCH_TARGET_PLATFORM", "lambda")


# API related configs
VERSION = "v1"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
APM_SERVER = os.getenv("APM_SERVER", None)
APM_SERVICE_NAME = os.getenv("APM_SERVICE_NAME", "deepdelve-backend")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# mcq indexing
SUPPORTED_BATCH_SIZE = os.getenv("SUPPORTED_BATCH_SIZE", 2000)
SUPPORTED_DATA_SIZE = os.getenv("SUPPORTED_DATA_SIZE", 500)
UPDATE_EXISTING_DOCUMENTS = os.getenv("UPDATE_EXISTING_DOCUMENTS", True)

# section_splitter_lambda name
SEARCH_LAMBDA_NAME = os.getenv("SEARCH_LAMBDA_NAME", "section_splitter_lambda")

# JWT variables
SECRET_KEY = "ae85228555d5ee5a8241be1de3c45817607ffbd7c2c89f59efd9a6a6fac5a59d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
