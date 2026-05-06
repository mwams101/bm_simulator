from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

import models

from database import engine
from modules import users, security, destination_schema, schema_fields, mapping_template, field_mapping, \
    field_mapping_details, uploaded_files, migration_jobs, migration_record, validation_result, \
    duplicate_detection, migration_report, notification, audit_log, new_bank_customer, new_bank_account



app = FastAPI()

# Ensure CORS headers are present even on unhandled 500 errors.
# Without this, Starlette's ServerErrorMiddleware returns the error response
# before CORSMiddleware can attach the Allow-Origin header.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

app.include_router(users.router)
app.include_router(security.router)
app.include_router(destination_schema.router)
app.include_router(schema_fields.router)
app.include_router(mapping_template.router)
app.include_router(field_mapping.router)
app.include_router(field_mapping_details.router)
app.include_router(uploaded_files.router)
app.include_router(migration_jobs.router)
app.include_router(migration_record.router)
app.include_router(validation_result.router)
app.include_router(duplicate_detection.router)
app.include_router(migration_report.router)
app.include_router(notification.router)
app.include_router(audit_log.router)
app.include_router(new_bank_customer.router)
app.include_router(new_bank_account.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)











