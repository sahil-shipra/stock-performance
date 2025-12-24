from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.api.main import router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0"
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
