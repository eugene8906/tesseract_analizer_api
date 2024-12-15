from fastapi import FastAPI
from app.routers.routers import router as rout

app = FastAPI()


app.include_router(rout)

