from rest_api.config import LOG_LEVEL
from rest_api.request.request import Organization, Survey
from rest_api.db.models.survey_insert_request import SurveyInsertRequest, SurveyMetaInsertRequest
from rest_api.db.schemas.survey_insert_request import SurvInsReqCreate, SurvMetaInsReqCreate, SurvUpReqCreate, \
    SurvMetaUpReqCreate
from rest_api.controller.utils import write_files_to_s3, delete_folder_from_s3, prefix_exists, write_json_to_s3
import logging
import pandas as pd
from io import StringIO
from datetime import datetime
from rest_api.db import crud
from sqlalchemy.orm import Session

df = pd.DataFrame()
logger = logging.getLogger('survey_insert')
logger.setLevel(LOG_LEVEL)


def check_if_survey_id_exist(db, org_id: str, survey_id: str):
    """

    :param db:
    :param org_id:
    :param survey_id:
    :return:
    """

    if crud.survey_insert_request.get_id(db=db, org_id=org_id, survey_id=survey_id):
        return True
    else:
        return False


def get_id_for_survey(db, org_id: str, survey_id: str):
    """

    :param db:
    :param org_id:
    :param survey_id:
    :return:
    """
    Id = crud.survey_insert_request.get_id(db=db, org_id=org_id, survey_id=survey_id)
    if Id:
        return Id
    else:
        return False


def get_s3_for_survey(db, org_id: str, survey_id: str):
    """

    :param db:
    :param org_id:
    :param survey_id:
    :return:
    """
    db_obj = crud.survey_insert_request.get(db=db, org_id=org_id, survey_id=survey_id)
    if db_obj:
        return db_obj.s3_file_path
    else:
        return False


def check_if_meta_of_survey_id_exist(db, req_id: int, meta_key: str):
    """

    :param req_id:
    :param db:
    :param meta_key:
    :return:
    """

    if crud.survey_meta_insert_request.get_meta_id(db=db, req_id=req_id, meta_key=meta_key):
        return True
    else:
        return False


def create_survey_insert_request(db: Session, org_id: str, survey_id: str, survey_description: str = None,
                                 file_path: str = None):
    """

    :param survey_description:
    :param survey_id:
    :param file_path:
    :param org_id:
    :param db:
    :return:
    """
    create_object = SurvInsReqCreate(orgId=org_id, surveyId=survey_id, surveyDescription=survey_description,
                                     s3_file_path=file_path)
    try:
        survey_ins_req = crud.survey_insert_request.create(db=db, obj_in=create_object)
        return survey_ins_req.id
    except Exception as e:
        logger.error(f"{survey_id}: storing in db failed : {e}")


def create_survey_delete_request(db: Session, id: int):
    """

    :param id:
    :param survey:
    :param survey_id:
    :param file_path:
    :param org_id:
    :param db:
    :return:
    """
    try:
        survey_delete_req = crud.survey_delete_request.remove(db=db, id=id)
        return survey_delete_req.id
    except Exception as e:
        logger.error(f"{id}: deleting in db failed : {e}")


def create_survey_meta_insert_request(db: Session, survey_req_id: int, meta_key: str = None,
                                      meta_value: str = None):
    """

    :param meta_key:
    :param survey_req_id:
    :param meta_value:
    :param db:
    :return:
    """
    create_object = SurvMetaInsReqCreate(surveyReqId=survey_req_id, metaKey=meta_key, metaValue=meta_value)
    try:
        survey_meta_ins_req = crud.survey_meta_insert_request.create(db=db, obj_in=create_object)
        return survey_meta_ins_req.id
    except Exception as e:
        logger.error(f"{survey_req_id}: storing in db failed : {e}")


def create_survey_meta_update_request(db: Session, survey_req_id: int, meta_key: str = None,
                                      meta_value: str = None):
    """

    :param req_id:
    :param meta_key:
    :param meta_value:
    :param survey:
    :param survey_id:
    :param file_path:
    :param org_id:
    :param db:
    :return:
    """
    db_obj = crud.survey_meta_update_request.get_meta(db=db, req_id=survey_req_id, meta_key=meta_key)
    # db_obj = crud.survey_meta_update_request.get(db=db, org_id=org_id, survey_id= survey_id, meta_key= meta_key)
    update_object = SurvMetaUpReqCreate(surveyReqId=survey_req_id, metaKey=meta_key, metaValue=meta_value)
    try:
        survey_meta_up_req = crud.survey_meta_update_request.update(db=db, db_obj=db_obj, obj_in=update_object)
        return survey_meta_up_req.id
    except Exception as e:
        logger.error(f"{survey_req_id}: updating in db failed : {e}")


def check_if_meta_exist(db: Session, org_id: str, org: Organization):
    org_id = org_id  # entity
    surveyList = org.surveyList
    meta_insert_list = []
    meta_update_list = []
    failed_surv = []
    success_surv = []
    for survey in surveyList:
        survey_id = survey.surveyId
        req_id = get_id_for_survey(db=db, org_id=org_id, survey_id=survey_id)
        # store meta in dictionary
        meta_data = survey.metaData
        for m in meta_data:
            meta_key = m.metaKey
            try:
                if check_if_meta_of_survey_id_exist(db, req_id=req_id[0], meta_key=meta_key):
                    meta_dict = {"surveyReqId": req_id[0], "metaKey": m.metaKey, "metaValue": m.value}
                    meta_update_list.append(meta_dict)
                else:
                    meta_dict = {"surveyReqId": req_id[0], "metaKey": m.metaKey, "metaValue": m.value}
                    meta_insert_list.append(meta_dict)
                success_surv.append({"id": survey_id})
            except Exception as e:
                failed_surv.append({"id": survey_id})
                logger.error(f"{survey_id}: Meta storage failed : {e}")

        return meta_insert_list, meta_update_list, success_surv, failed_surv


def available_for_delete(db: Session, org_id: str, org: Organization):
    org_id = org_id
    surveyList = org.surveyList
    survey_delete_list = []
    s3_list = []
    failed_surv = []
    success_surv = []
    for survey in surveyList:
        survey_id = survey.surveyId  # entity
        Id = get_id_for_survey(db, org_id, survey_id)
        if Id:
            s3_path = get_s3_for_survey(db, org_id, survey_id)
            s3_list.append(s3_path)
            success_surv.append({"id": survey_id})
            survey_delete_list.append(Id)
            logger.error(f"{survey_id}: survey_id exists for the org_id")
            continue
        else:
            failed_surv.append({"id": survey_id})
            logger.error(f"{survey_id}: survey_id doesnt exists for the org_id")

    return survey_delete_list, s3_list, success_surv, failed_surv


def delete_survey_from_s3(s3_list):
    failed_s3 = []
    for s3_path in s3_list:
        csv_path = s3_path
        s3_delete = delete_folder_from_s3(csv_path=csv_path)
        if not s3_delete:
            failed_s3.append(s3_path)
            logging.error(f"s3 folder failed to delete : {s3_path}")
    return failed_s3


def get_keys(survey: Survey):
    data = {}
    survey_data = survey.surveyData
    key_list = []
    surv_data_data = survey_data[0].Data
    for s_data in surv_data_data:
        key_list.append(str(s_data.key))  # entity
    data["keys"] = sorted(key_list)
    return data


def add_csv_to_s3(org_id: str, survey: Survey):
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")
    meta_list = []
    survey_df_list = []
    survey_id = survey.surveyId  # entity
    csv_file = "survey_data_" + org_id + "_" + survey_id + "_" + date + "_" + time + ".csv"
    json_file = "survey_data_" + org_id + "_" + survey_id + "_keys.json"
    csv_path = "survey_data/" + org_id + "/" + survey_id + "/"
    json_file_path = csv_path + json_file

    # check if data_keys file exists in s3
    data_keys = prefix_exists(json_file_path)
    json_keys = get_keys(survey=survey)
    # print(data_keys, json_keys)
    if data_keys:
        if data_keys != json_keys:
            logger.error(f"{survey_id}: Survey_id already exists for the org_id and keys are not same")
            return None, None, None

    survey_description = survey.surveyDescription  # entity
    # store meta in dictionary
    meta_data = survey.metaData
    for m in meta_data:
        meta_dict = {"orgId": org_id, "surveyId": survey_id, "metaKey": m.metaKey, "metaValue": m.value}
        meta_list.append(meta_dict)
    # store survey in s3
    survey_data = survey.surveyData
    for surv_data in survey_data:
        data = {}
        surv_data_id = surv_data.Id
        data["Id"] = surv_data_id
        surv_data_data = surv_data.Data
        for s_data in surv_data_data:
            surv_data_key = s_data.key
            surv_data_value = s_data.value
            data[surv_data_key] = surv_data_value
        survey_df_list.append(data)

    survey_df = pd.DataFrame(survey_df_list)
    csv_file_path = csv_path + csv_file
    csv_buffer = StringIO()
    survey_df.to_csv(csv_buffer, index=False)
    try:
        s3_path = write_files_to_s3(csv_file_path=csv_file_path, csv_buffer=csv_buffer, csv_path=csv_path)
        if s3_path:
            if json_keys and not data_keys:
                write_json_to_s3(json_file_path=json_file_path, json_object=json_keys)
                surv_dict = {"orgId": org_id, "surveyId": survey_id, "surveyDescription": survey_description,
                             "survey_s3_file_path": s3_path}
                return meta_list, surv_dict, False
            else:
                return None, None, True
        else:
            return None, None,
    except Exception as e:
        logger.error(f"{survey_id}: storing in s3 failed : {e}")
        return None, None, None
