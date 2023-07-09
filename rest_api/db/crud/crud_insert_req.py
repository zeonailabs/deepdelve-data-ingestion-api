from rest_api.db.crud.base import CRUDBase
from rest_api.db.models.survey_insert_request import SurveyInsertRequest, SurveyMetaInsertRequest
from rest_api.db.schemas.survey_insert_request import SurvInsReqCreate, SurvMetaInsReqCreate, SurvUpReqCreate, SurvMetaUpReqCreate
from sqlalchemy.orm import Session

#survey insert
class CRUDSurvInsReq(CRUDBase[SurveyInsertRequest, SurvInsReqCreate,SurvUpReqCreate]):
    def get(self, db: Session, org_id: str, survey_id: str):
        return db.query(self.model).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id)).first()

    def get_id(self, db: Session, org_id: str, survey_id: str):
        return db.query(self.model.id).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id)).first()

survey_insert_request = CRUDSurvInsReq(SurveyInsertRequest)
survey_update_request = CRUDSurvInsReq(SurveyInsertRequest)
survey_delete_request = CRUDSurvInsReq(SurveyInsertRequest)

#survey meta insert
class CRUDSurvMetaInsReq(CRUDBase[SurveyMetaInsertRequest, SurvMetaInsReqCreate,SurvMetaUpReqCreate]):
    def get(self, db: Session, org_id: str, survey_id: str):
        return db.query(self.model).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id)).first()

    def get_meta(self, db: Session, org_id: str, survey_id: str, meta_key: str):
        return db.query(self.model).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id) & (self.model.metaKey == meta_key)).first()
    
    def get_id(self, db: Session, org_id: str, survey_id: str):
        return db.query(self.model.id).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id)).first()
    
    def get_meta_id(self, db: Session, org_id: str, survey_id: str , meta_key: str):
        return db.query(self.model.id).filter((self.model.orgId == org_id) & (self.model.surveyId == survey_id) & (self.model.metaKey == meta_key)).first()
    
survey_meta_insert_request = CRUDSurvMetaInsReq(SurveyMetaInsertRequest)
survey_meta_update_request = CRUDSurvMetaInsReq(SurveyMetaInsertRequest)
