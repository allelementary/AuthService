from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.routers import auth, user
from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Hello World successfully deployd from CI/CD pipeline"}
