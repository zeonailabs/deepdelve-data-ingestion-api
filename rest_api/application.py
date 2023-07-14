import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from rest_api.router.errors.http_error import http_error_handler
from rest_api.router.router import router as api_router
from mangum import Mangum

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)
logging.getLogger("elasticsearch").setLevel(logging.WARNING)


def get_application() -> FastAPI:
    application = FastAPI(title="ZeonAI-API", debug=True, version="1.0")

    origins = [
        "*",
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(HTTPException, http_error_handler)
    application.include_router(api_router)
    return application


app = get_application()
handler = Mangum(app, lifespan="off")


# async def catch_exceptions_middleware(request: Request, call_next):
#    try:
#        return await call_next(request)
#    except Exception as e:
#        logger.info(e)
#        return PlainTextResponse("Something went wrong. Try again after sometime.", status_code=400)


# app.middleware('http')(catch_exceptions_middleware)

#handler = Mangum(app, lifespan="off")

#logger.info("Open http://127.0.0.1:8000/docs to see Swagger API Documentation.")

#if __name__ == "__main__":
#   uvicorn.run(app, host="0.0.0.0", port=8000)