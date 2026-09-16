import time
import uuid
import logging
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.routers import health, customers, payments

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
logger = logging.getLogger("minipay")

app = FastAPI(title="MiniPay API", version="1.0.0")

if settings.auto_create_tables:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas initialized successfully.")
    except Exception as e:
        logger.error(f"Error during schema generation block: {e}")

@app.middleware("http")
async def add_request_id_and_telemetry(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.info(f"Incoming Request [{request_id}] - Path: {request.url.path} Method: {request.method}")
    
    start_time = time.time()
    response: Response = await call_next(request)
    duration = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    logger.info(f"Completed Request [{request_id}] - Status: {response.status_code} Duration: {duration:.4f}s")
    return response

@app.exception_handler(Exception)
async def global_exception_interceptor(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", "UNKNOWN")
    logger.error(f"Unhandled operational system fault [{request_id}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNA_SERVER_ERROR, content={"error": "InternalServerError", "detail": "An unexpected server execution error occurred. Please reference your Request ID with support."}
    )

app.include_router(health.router)
app.include_router(customers.router)
app.include_router(payments.router)
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="app/ui", html=True), name="ui")
