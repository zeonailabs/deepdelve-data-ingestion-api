from rest_api.config import LOG_LEVEL, S3_BUCKET, S3_ACCESS_KEY_ID, S3_SECRET_KEY, AWS_REGION_VALUE
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
from collections import defaultdict
from typing import Dict, Any, List, Optional
import collections, copy
from sqlalchemy import or_, not_, and_
import boto3
from botocore.config import Config
import json

df = pd.DataFrame()
logger = logging.getLogger('survey_insert')
logger.setLevel(LOG_LEVEL)


def parser(filters: str):
    """
    parsed the input filter to a general form which can be easily converted 
    to other document_store specific forms.

    for ex- 
    filter= A AND B AND C OR D OR NOT E  AND NOT F C OR D OR NOT E

    parseds_filter output-:
    {
        '&':[A,B] ,
        '!' : [F] ,
        '|' : { {'|':[C,D] , '!' : [E] } ,{}}
    }
    """
    filters = filters.strip()
    array_and = filters.split('AND')
    array_and = [s.strip() for s in array_and]

    dic_and = collections.defaultdict(list)
    for i in array_and:
        if ' OR ' in i:
            dic_and['|'].append(i)
        elif 'NOT ' in i:
            dic_and['!'].append(i[4:])
        else:
            dic_and['&'].append(i)

    lst_or = []

    for i in dic_and['|']:

        dic = collections.defaultdict(list)

        i = i.split(' OR ')
        for j in i:
            if 'NOT ' not in j:
                dic['|'].append(j)
            else:
                dic['!'].append(j[4:])

        lst_or.append(dic)

    for i in lst_or:
        for j in i.keys():
            i[j] = parsed_by_parts(i[j])

    dic_and['|'] = lst_or
    dic_and['&'] = parsed_by_parts(dic_and['&'])
    dic_and['!'] = parsed_by_parts(dic_and['!'])

    return dic_and


def parsed_by_parts(filtr_lst: List):
    """
    helper function for parser function. To induct datatype , and other parameters.
    ex-
        filtr_lst= ["sub:'geography'", "exam:'upsccse'", 'score = 10']

        o/p= [{'key': 'sub', 'value': 'geography', 'dtype': 'string'},
                {'key': 'exam', 'value': 'upsccse', 'dtype': 'string'},
                {'key': 'score', 'value': 10.0, 'dtype': 'numeric', 'operation': {'type': '='}}
                ]
        
        filtr_lst=['date :10 TO 80']
        
        o/p= [{'key': 'date', 'dtype': 'numeric',
                    'operation': {'type': 'range', 'lower': 10.0, 'upper': 80.0}
                }]
    """

    chr = ['>=', '<=', '!=', '=', '<', '>']
    for i in range(len(filtr_lst)):
        s = filtr_lst[i].strip()
        if ':' in s:
            s = s.split(':')
            s[0] = s[0].strip()
            s[1] = s[1].strip()
            if 'TO' in s[1]:
                x = s[1].split('TO')
                try:
                    low = float(x[0].strip())
                    up = float(x[1].strip())
                except:
                    raise ValueError("can't covert {},{} to float".format(x[0], x[1]))
                filtr_lst[i] = {'key': s[0], 'dtype': 'numeric',
                                'operation': {'type': 'range', 'lower': low, 'upper': up}}

            elif s[1][0] == s[1][-1] == "'":
                filtr_lst[i] = {'key': s[0], 'value': s[1][1:-1], 'dtype': 'string'}
            elif s[1].lower() in ['true', 'false']:
                filtr_lst[i] = {'key': s[0], 'value': s[1].lower(), 'dtype': 'bool'}
            elif s[1][0] == '[':
                x = s[1][1:-1].split(',')
                if x[0][0] == "'":
                    x = [j[1:-1] for j in x]
                else:
                    x = [int(j) for j in x]
                filtr_lst[i] = {'key': s[0], 'value': x, 'dtype': 'array'}
            else:
                raise ValueError("string {} not recognized".format(s))
        elif any(c in s for c in chr):
            for c in chr:
                if c in s:
                    x = s.split(c)
                    filtr_lst[i] = {'key': x[0].strip(), 'value': float(x[1].strip()), 'dtype': 'numeric',
                                    'operation': {'type': c}}
                    break
        else:
            raise ValueError("string {} not recognized".format(s))

    return filtr_lst


def get_filtered_lists(filters: str):
    # Create the filter expressions
    # filters = defaultdict(list, {'&': [{'key': 'categories', 'value': 'politics', 'dtype': 'string'}, {'key': 'store', 'value': 'The Corner Bookshop', 'dtype': 'string'}], '|': [], '!': []})
    try:
        filters = parser(filters=filters)
        and_filters = []
        col1 = "metaKey"
        col2 = "metaValue"
        for filter_dict in filters.get('&', []):
            column_name = filter_dict['key']
            if filter_dict.get('value') != None:
                value = filter_dict['value']
            # print(column_name, " ", value)
            dtype = filter_dict['dtype']
            operation = filter_dict.get('operation')
            if dtype == 'string':
                and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                and_filters.append(getattr(SurveyMetaInsertRequest, col2) == value)
            if dtype == 'numeric' and operation:
                if operation['type'] == 'range':
                    lower = operation['lower']
                    upper = operation['upper']
                    and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    and_filters.append(getattr(SurveyMetaInsertRequest, col2).between(lower, upper))
                elif operation['type'] == '>=':
                    and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    and_filters.append(getattr(SurveyMetaInsertRequest, col2) >= value)
                elif operation['type'] == '<=':
                    and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    and_filters.append(getattr(SurveyMetaInsertRequest, col2) <= value)
                elif operation['type'] == '<':
                    and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    and_filters.append(getattr(SurveyMetaInsertRequest, col2) < value)
                elif operation['type'] == '>':
                    and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    and_filters.append(getattr(SurveyMetaInsertRequest, col2) > value)
                elif operation['type'] == '=':
                    and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    and_filters.append(getattr(SurveyMetaInsertRequest, col2) == value)
                elif operation['type'] == '!':
                    and_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    and_filters.append(getattr(SurveyMetaInsertRequest, col2) != value)

        or_filters = []
        for filter_dict_filt in filters.get('|', []):
            # print(filter_dict_filt)
            for filter_dict in filter_dict_filt.get('|', []):
                filt = []
                column_name = filter_dict['key']
                if filter_dict.get('value') != None:
                    value = filter_dict['value']
                dtype = filter_dict['dtype']
                # print(column_name, " ", dtype)
                if dtype == 'string':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) == value)
                    or_filters.append(and_(*filt))
                    # or_filters.append(getattr(SurveyMetaInsertRequest, col1) == column_name and getattr(SurveyMetaInsertRequest, col2) == value)
                if dtype == 'numeric' and operation:
                    if operation['type'] == 'range':
                        lower = operation['lower']
                        upper = operation['upper']
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2).between(lower, upper))
                        or_filters.append(and_(*filt))
                    elif operation['type'] == '>=':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) >= value)
                        or_filters.append(and_(*filt))
                    elif operation['type'] == '<=':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) <= value)
                        or_filters.append(and_(*filt))
                    elif operation['type'] == '<':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) < value)
                        or_filters.append(and_(*filt))
                    elif operation['type'] == '>':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) > value)
                        or_filters.append(and_(*filt))
                    elif operation['type'] == '=':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) == value)
                        or_filters.append(and_(*filt))
                    elif operation['type'] == '!':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) != value)
                        or_filters.append(and_(*filt))
            not_filters = []
            for filter_dict in filter_dict_filt.get('!', []):
                filt = []
                column_name = filter_dict['key']
                if filter_dict.get('value') != None:
                    value = filter_dict['value']
                dtype = filter_dict['dtype']
                # print(column_name, " ", dtype)
                if dtype == 'string':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) != value)
                    not_filters.append(and_(*filt))
                if dtype == 'numeric' and operation:
                    if operation['type'] == 'range':
                        lower = operation['lower']
                        upper = operation['upper']
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2).between(lower, upper))
                        not_filters.append(and_(*filt))
                    elif operation['type'] == '>=':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) >= value)
                        not_filters.append(and_(*filt))
                    elif operation['type'] == '<=':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) <= value)
                        not_filters.append(and_(*filt))
                    elif operation['type'] == '<':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) < value)
                        not_filters.append(and_(*filt))
                    elif operation['type'] == '>':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) > value)
                        not_filters.append(and_(*filt))
                    elif operation['type'] == '=':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) == value)
                        not_filters.append(and_(*filt))
                    elif operation['type'] == '!':
                        filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                        filt.append(getattr(SurveyMetaInsertRequest, col2) != value)
                        not_filters.append(and_(*filt))
            if not_filters:
                or_filters.append(not_(*not_filters))

        not_filters = []
        for filter_dict in filters.get('!', []):
            filt = []
            column_name = filter_dict['key']
            if filter_dict.get('value') != None:
                value = filter_dict['value']
            dtype = filter_dict['dtype']
            if dtype == 'string':
                filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                filt.append(getattr(SurveyMetaInsertRequest, col2) != value)
                not_filters.append(and_(*filt))
            if dtype == 'numeric' and operation:
                if operation['type'] == 'range':
                    lower = operation['lower']
                    upper = operation['upper']
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2).between(lower, upper))
                    not_filters.append(and_(*filt))
                elif operation['type'] == '>=':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) >= value)
                    not_filters.append(and_(*filt))
                elif operation['type'] == '<=':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) <= value)
                    not_filters.append(and_(*filt))
                elif operation['type'] == '<':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) < value)
                    not_filters.append(and_(*filt))
                elif operation['type'] == '>':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) > value)
                    not_filters.append(and_(*filt))
                elif operation['type'] == '=':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) == value)
                    not_filters.append(and_(*filt))
                elif operation['type'] == '!':
                    filt.append(getattr(SurveyMetaInsertRequest, col1) == column_name)
                    filt.append(getattr(SurveyMetaInsertRequest, col2) != value)
                    not_filters.append(and_(*filt))

        return [and_filters, or_filters, not_filters]
    except Exception as e:
        return None


def get_all_survey(db: Session, org_id: str, filters):
    """

    :param req_id:
    :param db:
    :param meta_key:
    :return:
    """

    if filters:
        surv_req_id_list = crud.survey_meta_insert_request.get_req_id_for_meta(db=db, filters=filters)
    else:
        surv_req_id_list = crud.survey_meta_insert_request.get_all_req_id_for_meta(db=db)

    if surv_req_id_list:
        surveyIdList = []
        surveys3List = []
        surveyIdListDict = []
        surveys = []
        for req_ids in surv_req_id_list:
            print(req_ids)
            surv = crud.survey_insert_request.get_all_req_id(db=db, org_id=org_id, req_ids=req_ids)
            if surv:
                surveys.append(surv)
        if surveys:
            for surv_list in surveys:
                for surv in surv_list:
                    print(surv.s3_file_path)
                    print(surv.surveyId)
                    surveyIdList.append(surv.surveyId)
                    surveyIdListDict.append({"surveyId": surv.surveyId})
                    surveys3List.append(surv.s3_file_path)
            return surveyIdListDict, surveyIdList, surveys3List
        else:
            return None, None, None
    else:
        return None, None, None


def check_survey_for_filters(db: Session, org_id: str, filters, surveyList: list):
    temp_surveyIdListDict, temp_surveyIdList, temp_surveys3List = get_all_survey(db=db, org_id=org_id, filters=filters)
    # print(surveyList)
    if temp_surveys3List:
        surveyIdListDict = []
        surveyIdList = []
        surveys3List = []
        for i, id in enumerate(temp_surveyIdList):
            if id in surveyList:
                # print(id, " ", temp_surveys3List[i])
                surveyIdListDict.append({"surveyId": id})
                surveyIdList.append(id)
                surveys3List.append(temp_surveys3List[i])
        return surveyIdListDict, surveyIdList, surveys3List
    else:
        return None, None, None


def predict_with_lambda(event: dict):
    """
    use model in tabular lambda
    """

    # test_event = {"request_id": "abcdef", "question": "value of hello", "s3_paths": ["s3://deepdelveclientdata/survey_data/1001/zeonaitest/"], "modelParameters":{"temperature": 0, "outputTokenLength": 0}}

    session = boto3.session.Session()
    config = Config(
        retries={
            'max_attempts': 1,
            'mode': 'standard',
        },
        read_timeout=840,
        connect_timeout=600
    )

    lambda_client = session.client(
        'lambda',
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=AWS_REGION_VALUE, config=config
    )
    try:
        response = lambda_client.invoke(
            FunctionName='tabularGenAi',
            Payload=json.dumps(event),
        )
        ans = json.loads(response['Payload'].read().decode("utf-8"))
        return ans

    except Exception as e:
        logging.error(e)
        return ""
