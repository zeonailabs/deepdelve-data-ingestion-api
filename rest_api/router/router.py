import imp
from fastapi import APIRouter

# from rest_api.router import auth_token

# from rest_api.router import content
# from rest_api.router import document_processing
# from rest_api.router import similar
# from rest_api.router import auth_token
from rest_api.router import survey_insert_api

router = APIRouter()

# router.include_router(content.router, tags=["Content-Api"])
# router.include_router(document_processing.router, tags=["Document-Processing-Api"])
# router.include_router(similar.router, tags=["Similarity-Api"])
# router.include_router(auth_token.router, tags=["Token"])
router.include_router(survey_insert_api.router, tags=["Survey-Api"])