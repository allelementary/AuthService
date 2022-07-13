from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.api import auth, user, router
from app.database import get_session

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.router)


@app.get("/")
async def root():
    return {"message": "Hello World successfully deployd from CI/CD pipeline"}
