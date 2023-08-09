from pathlib import Path
from typing import Literal
from io import BytesIO
import boto3
import json
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


def prefix_exists(json_file_path):
    s3_client = get_s3_client()

    try:
        res = s3_client.get_object(Bucket=S3_BUCKET, Key=json_file_path)
        if res:
            json_text = res["Body"].read().decode("utf-8")
            json_text_object = json.loads(json_text)
            return json_text_object
        else:
            return None

    except ClientError as ce:
        logging.error(ce)
        return None


def write_json_to_s3(json_file_path: str, json_object: dict):
    """

    :param json_object:
    :param json_file_path:
    :return:
    """
    s3_client = get_s3_client()

    try:
        s3_client.put_object(Body=json.dumps(json_object), Bucket=S3_BUCKET, Key=json_file_path)
        return 's3://' + S3_BUCKET + '/' + json_file_path
    except ClientError as e:
        logging.error(e)
        return ""


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
        # print("s3 successfull")
        return 's3://' + S3_BUCKET + '/' + csv_path
    except ClientError as e:
        logging.error(e)
        # print("s3 unsuccessfull")
        return ""


def delete_folder_from_s3(csv_path: str):
    """

    :param csv_path:
    :return:
    """
    s3_client = get_s3_client()
    csv_path = csv_path.replace(f"s3://{S3_BUCKET}/", "")
    try:
        objects = s3_client.list_objects(Bucket=S3_BUCKET, Prefix=csv_path)
        # print(objects)
        for object in objects['Contents']:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=object['Key'])
        s3_client.delete_object(Bucket=S3_BUCKET, Key=csv_path)
        return True
    except ClientError as e:
        logging.error(e)
        return False
