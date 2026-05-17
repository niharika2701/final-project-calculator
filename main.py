from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from app.database import get_engine
from app import models
from app.routers import users, calculations, auth, reports
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Module 13 - JWT Auth API")

models.Base.metadata.create_all(bind=get_engine())

app.include_router(users.router)
app.include_router(calculations.router)
app.include_router(auth.router)
app.include_router(reports.router)

templates = Jinja2Templates(directory="templates")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {errors}")
    return JSONResponse(status_code=400, content={"error": errors})


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


@app.get("/calculations")
async def calculations_page(request: Request):
    return templates.TemplateResponse(request=request, name="calculations.html")

@app.get("/reports")
async def reports_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports.html")
