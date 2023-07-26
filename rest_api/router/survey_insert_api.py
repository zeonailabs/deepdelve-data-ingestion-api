import logging
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from rest_api.request.request import Organization, OrganizationMeta, OrganizationSurvey, OrganizationSearch, OrganizationStatus, OrganizationFeedback
from rest_api.response.response import InsertAPIResponse, UpdateAPIResponse, DeleteAPIResponse, Message, SearchAPIResponse, StatusAPIResponse, FeedbackAPIResponse
from rest_api.controller.survey_insert import check_if_search_id_exists, create_survey_feedback_insert_request, get_status, check_if_survey_id_exist, create_survey_update_request, add_csv_to_s3, available_for_delete, create_survey_insert_request, \
    create_survey_delete_request, create_survey_meta_insert_request, create_survey_meta_update_request, \
    check_if_meta_exist, delete_survey_from_s3, create_search_insert_request, create_survey_search_update_request
from rest_api.controller.survey_search import get_all_survey, check_survey_for_filters, get_filtered_lists, predict_with_lambda
from rest_api.controller import get_survey_db
from rest_api.router import auth_token
from rest_api.config import LOG_LEVEL, SUPPORTED_DATA_SIZE, VERSION

logger = logging.getLogger('survey_insert')
logger.setLevel(LOG_LEVEL)
router = APIRouter()


@router.post("/" + VERSION + "/deepdelve/survey/insert", response_model=InsertAPIResponse,
             responses={400: {"model": Message}, 413: {"model": Message}, 501: {"model": Message}},
             response_model_exclude_unset=True)
async def submit_survey(response: Response, org: Organization,
                        db: Session = Depends(get_survey_db.get_db),
                        current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id

    if not org:
        logger.error(f"{unique_id}: Null organisation request")
        return JSONResponse(status_code=400, content={"message": "Empty payload"})

    total_data_points = 0
    for survlst in org.surveyList:
        total_data_points += len(survlst.surveyData)
    print("total_data_points = ", total_data_points)
    if total_data_points > SUPPORTED_DATA_SIZE:
        logger.error(f"{unique_id}: Input Request too long")
        return JSONResponse(status_code=413, content={"message": "Number of survey requests are more than allowed "
                                                                 "data size"})
    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    success_surv = []
    failed_surv = []
    for survey in org.surveyList:
        no_of_rows = len(survey.surveyData)
        print(no_of_rows)
        meta_list, surv_dict, survey_present = add_csv_to_s3(org_id=org_id, survey=survey)
        if surv_dict:
            surv_ins_id = create_survey_insert_request(db=db, org_id=org_id, survey_id=survey.surveyId,
                                                       survey_description=surv_dict["surveyDescription"],
                                                       file_path=surv_dict["survey_s3_file_path"],
                                                       total_no_of_rows= no_of_rows)

            for dict in meta_list:
                meta_ins_id = create_survey_meta_insert_request(db=db, survey_req_id=surv_ins_id,
                                                                meta_key=dict["metaKey"],
                                                                meta_value=dict["metaValue"])
            success_surv.append({"id": survey.surveyId})
        elif survey_present:
            dbj = check_if_survey_id_exist(db =db , org_id= org_id, survey_id = survey.surveyId)
            if dbj:
                prev_no = dbj.total_no_of_rows or 0
                surv_ins_id = create_survey_update_request(db=db, org_id= org_id, survey_id = survey.surveyId, total_no_of_rows= no_of_rows+prev_no)
                success_surv.append({"id": survey.surveyId})
            else:
                failed_surv.append({"id": survey.surveyId})
            
        else:
            failed_surv.append({"id": survey.surveyId})

    return {"status": {"success": True, "code": 200}, "message": "Request successfully received",
            "successSurveyIds": success_surv, "failedSurveyIds": failed_surv}


@router.post("/" + VERSION + "/deepdelve/survey/metaupdate", response_model=UpdateAPIResponse,
             responses={400: {"model": Message}, 413: {"model": Message}, 501: {"model": Message}},
             response_model_exclude_unset=True)
async def update_surveymeta(response: Response, org: OrganizationMeta,
                            db: Session = Depends(get_survey_db.get_db),
                            current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id  # entity
    # org_id = "1001"  # entity
    if not org:
        logger.error(f"{unique_id}: Null update request")
        return JSONResponse(status_code=400, content={"message": "Empty payload"})

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
        return JSONResponse(status_code=501, content={"message": "Data Updation Unsuccessful"})


@router.post("/" + VERSION + "/deepdelve/survey/delete", response_model=DeleteAPIResponse,
             responses={400: {"model": Message}, 410: {"model": Message}, 501: {"model": Message}},
             response_model_exclude_unset=True)
async def delete_survey(response: Response, org: OrganizationSurvey,
                        db: Session = Depends(get_survey_db.get_db),
                        current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id  # entity
    # org_id = "1001" # entity
    if not org:
        logger.error(f"{unique_id}: Null delete request")
        return JSONResponse(status_code=400, content={"message": "Empty payload"})

    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    survey_delete_list, s3_list, success_surv, failed_surv = available_for_delete(db=db, org_id=org_id, org=org)
    if survey_delete_list:
        # todo - populate the database for survey and meta
        for id in survey_delete_list:
            meta_ins_id = create_survey_delete_request(db=db, id=id)
        stats = delete_survey_from_s3(s3_list)
        if stats:
            logger.error(f"{stats}: s3_folder deletion failed")
            return JSONResponse(status_code=501, content={"message": "Data Deletion Unsuccessful"})

        return {"status": {"success": True, "code": 200}, "message": "Request successfully received",
                "successSurveyIds": success_surv, "failedSurveyIds": failed_surv}
    else:
        logger.error(f"{unique_id}: Data deletion failed")
        return JSONResponse(status_code=501, content={"message": "Data Deletion Unsuccessful"})


@router.post("/" + VERSION + "/deepdelve/survey/search", response_model=SearchAPIResponse,
             responses={400: {"model": Message}, 410: {"model": Message}, 501: {"model": Message}},
             response_model_exclude_unset=True)
async def search_survey(response: Response, org: OrganizationSearch,
                        db: Session = Depends(get_survey_db.get_db),
                        current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id  # entity
    # org_id = "1001" # entity
    if not org:
        logger.error(f"{unique_id}: Null search request")
        return JSONResponse(status_code=400, content={"message": "Empty payload"})

    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    question = org.question
    filters_str = org.filters
    model_parameters = org.modelParameters
    if not filters_str:
        logger.error(f"{unique_id}: Null filters in search request")
        return JSONResponse(status_code=400, content={"message": "Empty filters in payload"})
    filters = get_filtered_lists(filters_str)
    survey = org.surveyList
    surveyList = []
    for surv in survey:
        surveyList.append(surv.surveyId)
    
    if not surveyList:
        surveyIdListDict, surveyIdList, surveys3List = get_all_survey(db = db, filters = filters)
    
    else:
        surveyIdListDict, surveyIdList, surveys3List = check_survey_for_filters(db = db , filters = filters, surveyList = surveyList)
    
    # print(surveyIdList, surveys3List)
    if surveys3List:
        req_id = create_search_insert_request(db = db, searchId= unique_id, orgId= org_id, question= question, answer = "answer not found", inputSurveyIdList= str(surveyList), filters= filters_str, filteredSurveyIdList= str(surveyIdList), modelParameter= str(model_parameters.__dict__), calculationDescription= "description not found" )
        #todo - call answer lambda 
        test_event = {"request_id": unique_id, "question": question, "s3_paths": surveys3List, "modelParameters":model_parameters.__dict__}
        # print(test_event)
        response = predict_with_lambda(event= test_event)
        answer = response["body"]["output"]["answer"]
        cal_desc = response["body"]["output"]["calculation_description"]
        # print(response)
        # print(answer, cal_desc)
        up_req_id = create_survey_search_update_request(db = db, id= req_id, searchId= unique_id , answer= answer , calculationDescription= cal_desc)
        return {"status": {"success": True, "code": 200}, "message": "Request successfully received, search successfully done",
                "answer": answer or "", "surveyList": surveyIdListDict}
        
    else:
        logger.error(f" no survey found for this filter: {filters}")
        return JSONResponse(status_code=501, content={"message": "no survey found for this filter, filters search Unsuccessful"})
    
    #todo - call answer lambda 


@router.post("/" + VERSION + "/deepdelve/survey/status", response_model=StatusAPIResponse,
             responses={400: {"model": Message}, 410: {"model": Message}, 501: {"model": Message}},
             response_model_exclude_unset=True)
async def survey_status(response: Response, org: OrganizationStatus,
                        db: Session = Depends(get_survey_db.get_db),
                        current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id  # entity
    # org_id = "1001" # entity
    if not org:
        logger.error(f"{unique_id}: Null delete request")
        return JSONResponse(status_code=400, content={"message": "Empty payload"})

    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    survey_id = org.surveyId
    survey_present = check_if_survey_id_exist(db=db, org_id= org_id, survey_id= survey_id)
    if survey_present:
        # todo - populate the database for survey and meta
        resp = get_status(db =db, org_id = org_id, survey_id = survey_id, db_object= survey_present)
        if not resp:
            logger.error(f"{unique_id}: no survey data found")
            return JSONResponse(status_code=501, content={"message": "Find Survey Data Status Unsuccessful"})
        
        return {"status": {"success": True, "code": 200}, "message": f"Request successfully received, survey found for survey_id {survey_id}",
                "dataPresent": True, "surveyData": resp}
    else:
        logger.error(f"{unique_id}: no survey found")
        return {"status": {"success": True, "code": 200}, "message": f"Request successfully received, survey NOT found for survey_id {survey_id}",
                "dataPresent": False, "surveyData": {}}

@router.post("/" + VERSION + "/deepdelve/survey/feedback", response_model=FeedbackAPIResponse,
             responses={400: {"model": Message}, 410: {"model": Message}, 501: {"model": Message}},
             response_model_exclude_unset=True)
async def survey_feedback(response: Response, org: OrganizationFeedback,
                        db: Session = Depends(get_survey_db.get_db),
                        current_user: auth_token.User = Depends(auth_token.get_current_active_user)):
    unique_id = str(uuid4())
    org_id = current_user.org_id  # entity
    # org_id = "1001" # entity
    if not org:
        logger.error(f"{unique_id}: Null delete request")
        return JSONResponse(status_code=400, content={"message": "Empty payload"})

    response.headers["X-ZAI-REQUEST-ID"] = unique_id
    response.headers["X-ZAI-ORG-ID"] = org_id
    search_id = org.searchId
    feedback = org.feedback
    feedback_details = org.feedbackDetails
    search_req_id = check_if_search_id_exists(db = db, search_id = search_id)
    if search_req_id:
        print(feedback_details)
        if feedback == "like":
            option = feedback_details.like.option
            remark = feedback_details.like.remarks
        elif feedback == "dislike":
            option = feedback_details.dislike.option
            remark = feedback_details.dislike.remarks
        feed_id = create_survey_feedback_insert_request(db =db, searchId = search_id, searchReqId = search_req_id[0], feedback = feedback, option = option, remarks = remark)
        if not feed_id:
            logger.error(f"{unique_id}: feedback storing failed")
            return JSONResponse(status_code=501, content={"message": "Find Survey Data Status Unsuccessful"})
        return {"status": {"success": True, "code": 200}, "message": "Feedback successfully received"}
    else:
        logger.error(f"{unique_id}: no search history found")
        return JSONResponse(status_code=501, content={"message": "Search id doesnt exist"})
