import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import os
import datetime
import uuid


load_dotenv()


inngest_client = inngest.Client(
    app_id = "rag_app",
    logging = logging.getLogger("uvicorn"),
    is_production = False,
    serializer = inngest.PydanticSerializer(),
)

app = FastAPI()
inngest.fast_api.serve(app, inngest_client)