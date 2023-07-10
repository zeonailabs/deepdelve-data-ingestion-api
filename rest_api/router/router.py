from fastapi import APIRouter
from rest_api.router import survey_insert_api
from rest_api.router import auth_token

router = APIRouter()

router.include_router(survey_insert_api.router, tags=["Survey-Api"])
router.include_router(auth_token.router, tags=["Token"])