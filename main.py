# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/get_movie", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("page.html", {"request": request})


