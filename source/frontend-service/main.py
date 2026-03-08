import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Mars Frontend Service")

# Setup template directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """
    Serves the index.html file.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/rules", response_class=HTMLResponse)
async def read_rules(request: Request):
    """
    Serves the rules.html file.
    """
    return templates.TemplateResponse("rules.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}

