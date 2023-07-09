from fastapi import APIRouter
from rest_api.router import survey_insert_api

router = APIRouter()

router.include_router(survey_insert_api.router, tags=["Survey-Api"])