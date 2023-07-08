import logging
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Union, List, Optional, Dict, Generator
from sqlalchemy.orm import Session
from rest_api.request.request import Organization
from rest_api.response.response import InsertAPIResponse, UpdateAPIResponse
from rest_api.controller.survey_insert import add_csv_to_s3, create_survey_insert_request, create_survey_meta_insert_request
from rest_api.controller import get_survey_db
from rest_api.router import auth_token
from rest_api.config import VERSION, SUPPORTED_BATCH_SIZE, LOG_LEVEL,  SUPPORTED_DATA_SIZE


logger = logging.getLogger('survey_insert')
logger.setLevel(LOG_LEVEL)
router = APIRouter()


@router.post("/v1/deepdelve/survey/insert/", response_model=InsertAPIResponse,
             response_model_exclude_unset=True)
async def submit_survey(org: Organization, response: Response,
                            db: Session = Depends(get_survey_db.get_db)):
    unique_id = str(uuid4())
    org_id = org.orgId    #entity
    if not org:
        logger.error(f"{unique_id}: Null organisation request")
        raise HTTPException(status_code=414, detail="Organisation request payload is empty")
    
    total_data_points = 0
    for surv in org.surveyList:
        for data in surv.surveyData:
            total_data_points += 1
    # print(total_data_points)
    
    if total_data_points > SUPPORTED_DATA_SIZE:
        logger.error(f"{unique_id}: Input Request too long")
        raise HTTPException(status_code=413, detail="Number of requests are more than allowed data size")
    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id

    meta_list, surv_s3_list , success_surv, failed_surv = add_csv_to_s3(org = org, db = db)
    # print(surv_s3_list)
    # print(meta_list)
    if surv_s3_list or meta_list:

        #todo - populate the database for survey
        for dict in surv_s3_list:
            surv_ins_id = create_survey_insert_request(db = db, org_id = dict["orgId"] , survey_id= dict["surveyId"], survey_description=dict["surveyDescription"], file_path= dict["survey_s3_file_path"])
        
        #todo - populate the database for meta
        for dict in meta_list:
            meta_ins_id = create_survey_meta_insert_request(db = db, org_id = dict["orgId"] , survey_id= dict["surveyId"], meta_key=dict["metaKey"], meta_value= dict["metaValue"])
        
        return {"status": {"success": True, "code": 200}, "message": "Request successfully received", "successSurveyIds" : success_surv, "failedSurveyIds" : failed_surv}
    else:
        logger.error(f"{unique_id}: storing in s3 failed")
        raise HTTPException(status_code=501, detail="data addition in s3 can not be done")

@router.post("/v1/deepdelve/survey/metaupdate/", response_model=UpdateAPIResponse,
             response_model_exclude_unset=True)
async def update_surveymeta(org: Organization, response: Response,
                            db: Session = Depends(get_survey_db.get_db)):
    unique_id = str(uuid4())
    org_id = org.orgId    #entity
    if not org:
        logger.error(f"{unique_id}: Null create request")
        raise HTTPException(status_code=414, detail="Create request payload is empty")
    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    meta_list, surv_s3_list = add_csv_to_s3(org = org)
    print(surv_s3_list)
    print(meta_list)
    if meta_list:

        #todo - populate the database for meta
        for dict in meta_list:
            meta_ins_id = create_survey_meta_insert_request(db = db, org_id = dict["orgId"] , survey_id= dict["surveyId"], meta_key=dict["metaKey"], meta_value= dict["metaValue"])
        
        return {"status": {"success": True, "code": 200}, "message": "Request successfully received"}
    else:
        logger.error(f"{unique_id}: storing in s3 failed")
        raise HTTPException(status_code=501, detail="data addition in s3 can not be done")