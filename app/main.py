from contextlib import asynccontextmanager
import os
from fastapi.middleware.cors import CORSMiddleware
from services.observability import DEVELOPMENT_MODE, PRODUCTION_MODE, get_logger, initialize_observability, instrument_application
from routers.translate import translate_router
from routers.feedback import feedback_router
from routers.evaluation import evaluation_router
from fastapi import FastAPI
from dotenv import load_dotenv
import services.azoai as azoai
load_dotenv()

# This method controls the lifecycle of the FastAPI app and is used to setup things post process fork
# https://fastapi.tiangolo.com/advanced/events/#use-case
@asynccontextmanager
async def lifespan(app: FastAPI):
    app_environment = os.getenv("APP__ENVIRONMENT", "Unspecified")
    # do the initialize logic here

    if app_environment.lower() == "development":
        initialize_observability(DEVELOPMENT_MODE, service_name="AI Translator API", environment=app_environment)
    else:
        initialize_observability(PRODUCTION_MODE, service_name="AI Translator API", environment=app_environment)

    azoai.setup()
    logger = get_logger()
    logger.info("Starting API server...")
    yield
    logger.info("Stopping API server...")


app = FastAPI(
    title="AI Translate",
    description="This is a simple API that translates text from one language to another",
    version="0.1.0",
    lifespan=lifespan,
)

# middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add the frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(translate_router)
app.include_router(feedback_router)
app.include_router(evaluation_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the ai translate!"}

instrument_application(app)
