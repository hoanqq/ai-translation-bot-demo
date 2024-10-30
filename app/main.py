from fastapi.middleware.cors import CORSMiddleware
from routers.translate import translate_router
from routers.feedback import feedback_router
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

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


@app.get("/")
def read_root():
    return {"message": "Welcome to the ai translate!"}
