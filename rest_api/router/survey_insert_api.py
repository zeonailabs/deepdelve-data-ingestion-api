import logging
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from rest_api.request.request import Organization, OrganizationMeta, OrganizationSurvey
from rest_api.response.response import InsertAPIResponse, UpdateAPIResponse, DeleteAPIResponse
from rest_api.controller.survey_insert import add_csv_to_s3, available_for_delete, create_survey_insert_request, \
    create_survey_delete_request, create_survey_meta_insert_request, create_survey_meta_update_request, \
    check_if_meta_exist, delete_survey_from_s3
from rest_api.controller import get_survey_db
from rest_api.router import auth_token
from rest_api.config import LOG_LEVEL, SUPPORTED_DATA_SIZE, VERSION

logger = logging.getLogger('survey_insert')
logger.setLevel(LOG_LEVEL)
router = APIRouter()


@router.post("/" + VERSION + "/deepdelve/survey/insert", response_model=InsertAPIResponse,
             response_model_exclude_unset=True)
async def submit_survey(response: Response, org: Organization,
                        db: Session = Depends(get_survey_db.get_db),
                        current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id

    if not org:
        logger.error(f"{unique_id}: Null organisation request")
        raise HTTPException(status_code=414, detail="Organisation request payload is empty")

    total_data_points = 0
    for survlst in org.surveyList:
        for survdata in survlst.surveyData:
            total_data_points += len(survdata.Data)

    if total_data_points > SUPPORTED_DATA_SIZE:
        logger.error(f"{unique_id}: Input Request too long")
        raise HTTPException(status_code=413, detail="Number of survey requests are more than allowed data size")
    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id

    meta_list, surv_s3_list, success_surv, failed_surv = add_csv_to_s3(org_id=org_id, org=org, db=db)
    if surv_s3_list or meta_list:

        # todo - populate the database for survey
        for dict in surv_s3_list:
            surv_ins_id = create_survey_insert_request(db=db, org_id=dict["orgId"], survey_id=dict["surveyId"],
                                                       survey_description=dict["surveyDescription"],
                                                       file_path=dict["survey_s3_file_path"])

        # todo - populate the database for meta
        for dict in meta_list:
            meta_ins_id = create_survey_meta_insert_request(db=db, survey_req_id=surv_ins_id,
                                                            meta_key=dict["metaKey"], meta_value=dict["metaValue"])

        return {"status": {"success": True, "code": 200}, "message": "Request successfully received",
                "successSurveyIds": success_surv, "failedSurveyIds": failed_surv}
    else:
        logger.error(f"{unique_id}: storing in s3 failed")
        raise HTTPException(status_code=501, detail="Data Ingestion unsuccessful")


@router.post("/" + VERSION + "/deepdelve/survey/metaupdate", response_model=UpdateAPIResponse,
             response_model_exclude_unset=True)
async def update_surveymeta(response: Response, org: OrganizationMeta,
                            db: Session = Depends(get_survey_db.get_db),
                            current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id  # entity
    # org_id = "1001"  # entity
    if not org:
        logger.error(f"{unique_id}: Null update request")
        raise HTTPException(status_code=414, detail="Upload request payload is empty")
    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    meta_insert_list, meta_update_list, success_surv, failed_surv = check_if_meta_exist(db=db, org_id=org_id, org=org)
    if meta_insert_list or meta_update_list:
        # todo - populate the database for meta
        for dict in meta_update_list:
            meta_ins_id = create_survey_meta_update_request(db=db, survey_req_id=dict["surveyReqId"],
                                                            meta_key=dict["metaKey"], meta_value=dict["metaValue"])

        # todo - populate the database for meta
        for dict in meta_insert_list:
            meta_ins_id = create_survey_meta_insert_request(db=db, survey_req_id=dict["surveyReqId"],
                                                            meta_key=dict["metaKey"], meta_value=dict["metaValue"])

        return {"status": {"success": True, "code": 200}, "message": "Request successfully received",
                "successSurveyIds": success_surv, "failedSurveyIds": failed_surv}
    else:
        logger.error(f"{unique_id}: Data updation unsuccessful")
        raise HTTPException(status_code=501, detail="Data updation unsuccessful")


@router.post("/" + VERSION + "/deepdelve/survey/delete", response_model=DeleteAPIResponse,
             response_model_exclude_unset=True)
async def delete_survey(response: Response, org: OrganizationSurvey,
                        db: Session = Depends(get_survey_db.get_db),
                        current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id  # entity
    # org_id = "1001" # entity
    if not org:
        logger.error(f"{unique_id}: Null update request")
        raise HTTPException(status_code=414, detail="Upload request payload is empty")
    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    survey_delete_list, s3_list,  success_surv, failed_surv = available_for_delete(db=db, org_id=org_id, org=org)
    if survey_delete_list:
        # todo - populate the database for survey and meta
        for id in survey_delete_list:
            meta_ins_id = create_survey_delete_request(db=db, id=id)
        stats = delete_survey_from_s3(s3_list)
        if stats:
            logger.error(f"{stats}: s3_folder deletion failed")
            raise HTTPException(status_code=501, detail="s3 folder deletion unsuccessful")
        
        return {"status": {"success": True, "code": 200}, "message": "Request successfully received",
                "successSurveyIds": success_surv, "failedSurveyIds": failed_surv}
    else:
        logger.error(f"{unique_id}: Data deletion failed")
        raise HTTPException(status_code=501, detail="Data deletion unsuccessful")
