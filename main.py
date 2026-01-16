from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import models

from database import engine
from modules import users, security, destination_schema, schema_fields, mapping_template

# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(security.router)
app.include_router(destination_schema.router)
app.include_router(schema_fields.router)
app.include_router(mapping_template.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)











