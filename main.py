from fastapi import FastAPI

import models

from database import engine
from modules import users


models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)











