from rest_api.db.crud.base import CRUDBase
from rest_api.db.models.survey_insert_request import SurveyInsertRequest, SurveyMetaInsertRequest, SurveySearchInsertRequest, SurveyFeedbackInsertRequest
from rest_api.db.schemas.survey_insert_request import SurvInsReqCreate, SurvMetaInsReqCreate, SurvUpReqCreate, SurvMetaUpReqCreate, SurvSearchInsReqCreate, SurvSearchUpReqCreate, SurvFeedInsReqCreate, SurvFeedUpReqCreate
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, not_ 


# survey insert
class CRUDSurvInsReq(CRUDBase[SurveyInsertRequest, SurvInsReqCreate, SurvUpReqCreate]):
    def get(self, db: Session, org_id: str, survey_id: str):
        return db.query(self.model).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id)).first()

    def get_id(self, db: Session, org_id: str, survey_id: str):
        return db.query(self.model.id).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id)).first()

    def get_all_req_id(self, db: Session, req_ids: tuple):
        return db.query(self.model).filter((self.model.id.in_(req_ids))).all()


survey_insert_request = CRUDSurvInsReq(SurveyInsertRequest)
survey_update_request = CRUDSurvInsReq(SurveyInsertRequest)
survey_delete_request = CRUDSurvInsReq(SurveyInsertRequest)


# survey meta insert
class CRUDSurvMetaInsReq(CRUDBase[SurveyMetaInsertRequest, SurvMetaInsReqCreate, SurvMetaUpReqCreate]):
    def get(self, db: Session, req_id: int):
        return db.query(self.model).filter((self.model.surveyReqId == req_id)).all()

    def get_meta(self, db: Session, req_id: int, meta_key: str):
        return db.query(self.model).filter((self.model.surveyReqId == req_id) & (
                self.model.metaKey == meta_key)).first()

    def get_id(self, db: Session, req_id: int):
        return db.query(self.model.id).filter((self.model.surveyReqId == req_id)).first()

    def get_meta_id(self, db: Session, req_id: int, meta_key: str):
        return db.query(self.model.id).filter(
            (self.model.surveyReqId == req_id) & (self.model.metaKey == meta_key)).first()
    
    def get_req_id_for_meta(self, db: Session, filters):
        if filters[2]:
            return db.query(self.model.surveyReqId).filter(and_(*filters[0])).filter(or_(*filters[1])).filter(not_(*filters[2])).all()
        else:
            return db.query(self.model.surveyReqId).filter(and_(*filters[0])).filter(or_(*filters[1])).all()


survey_meta_insert_request = CRUDSurvMetaInsReq(SurveyMetaInsertRequest)
survey_meta_update_request = CRUDSurvMetaInsReq(SurveyMetaInsertRequest)

class CRUDSurvSearchInsReq(CRUDBase[SurveySearchInsertRequest, SurvSearchInsReqCreate, SurvSearchUpReqCreate]):
    def get(self, db: Session, org_id: str, search_id: str):
        return db.query(self.model).filter((self.model.orgId == org_id) & (self.model.searchId == search_id)).first()

    def get_id(self, db: Session, org_id: str, search_id: str):
        return db.query(self.model.id).filter((self.model.orgId == org_id) & (self.model.searchId == search_id)).first()

    def get_by_id(self, db: Session, id):
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_search(self, db: Session, search_id: str):
        return db.query(self.model.id).filter(self.model.searchId == search_id).first()


survey_search_insert_request = CRUDSurvSearchInsReq(SurveySearchInsertRequest)
survey_search_update_request = CRUDSurvSearchInsReq(SurveySearchInsertRequest)
survey_search_delete_request = CRUDSurvSearchInsReq(SurveySearchInsertRequest)

class CRUDSurvFeedbackInsReq(CRUDBase[SurveyFeedbackInsertRequest, SurvFeedInsReqCreate, SurvFeedUpReqCreate]):
    def get(self, db: Session, org_id: str, search_id: str):
        return db.query(self.model).filter((self.model.orgId == org_id) & (self.model.searchId == search_id)).first()

    def get_id(self, db: Session, search_id: str):
        return db.query(self.model.id).filter(self.model.searchId == search_id).first()

    def get_by_id(self, db: Session, id):
        return db.query(self.model).filter(self.model.id == id).first()


survey_feedback_insert_request = CRUDSurvFeedbackInsReq(SurveyFeedbackInsertRequest)
survey_feedback_update_request = CRUDSurvFeedbackInsReq(SurveyFeedbackInsertRequest)
survey_feedback_delete_request = CRUDSurvFeedbackInsReq(SurveyFeedbackInsertRequest)
