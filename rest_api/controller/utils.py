from pathlib import Path
from typing import Literal
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
import logging
from rest_api.config import S3_ACCESS_KEY_ID, S3_SECRET_KEY, AWS_REGION_VALUE, LOG_LEVEL, S3_BUCKET

logger = logging.getLogger('Generative-API')
logger.setLevel(LOG_LEVEL)

supported_files = [".docx", ".doc", ".pdf"]


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def is_file_type_supported(file_name: str = None):
    """

    :param file_name:
    :return:
    """

    if Path(file_name).suffix.lower() in supported_files:
        return True
    else:
        return False


def get_s3_client():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_KEY)
    return s3_client


def write_file_to_s3(file_obj, bucket_name: str, org_id: str, doc_id: str, file_name: str,
                     request_type: Literal["question_generation", "summarization"]):
    """

    :param file_name:
    :param bucket_name:
    :param file_obj:
    :param org_id:
    :param doc_id:
    :param request_type:
    :return:
    """
    s3_client = get_s3_client()
    file_path = request_type + "/" + org_id + "/" + doc_id + "/" + file_name
    fo = BytesIO(file_obj.read())
    try:
        s3_client.upload_fileobj(fo, bucket_name, file_path)
    except ClientError as e:
        logging.error(e)

    return 's3://' + bucket_name + '/' + file_path


def write_files_to_s3(csv_file_path: str, csv_buffer, csv_path: str):
    """

    :param csv_buffer:
    :param csv_path:
    :param csv_file_path:
    :return:
    """
    s3_client = get_s3_client()

    try:
        s3_client.put_object(Body=csv_buffer.getvalue(), Bucket=S3_BUCKET, Key=csv_file_path)
    except ClientError as e:
        logging.error(e)

    return 's3://' + S3_BUCKET + '/' + csv_path
