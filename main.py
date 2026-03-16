from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import models

from database import engine
from modules import users, security, destination_schema, schema_fields, mapping_template, field_mapping, \
    field_mapping_details, uploaded_files, migration_jobs

# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(security.router)
app.include_router(destination_schema.router)
app.include_router(schema_fields.router)
app.include_router(mapping_template.router)
app.include_router(field_mapping.router)
app.include_router(field_mapping_details.router)
app.include_router(uploaded_files.router)
app.include_router(migration_jobs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)











