from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator
from datetime import datetime
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



class Task(BaseModel):
    tag: str
    date: str  # e.g. "2025-08-03 15"
    priority: int

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        try:
            # parse browser datetime-local format
            dt = datetime.strptime(v, "%Y-%m-%dT%H:%M")
            # convert to your required format
            return dt.strftime("%Y-%m-%d %H")
        except ValueError:
            raise ValueError("Date must be in 'YYYY-MM-DD HH' format")


TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    tasks = load_tasks()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})


@app.post("/add")
async def add_task(tag: str = Form(...), date: str = Form(...), priority: int = Form(...)):
    tasks = load_tasks()
    task = Task(tag=tag, date=date, priority=priority)
    tasks.append(task.dict())
    save_tasks(tasks)
    return RedirectResponse("/", status_code=302)


@app.post("/remove")
async def remove_task(tag: str = Form(...)):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["tag"] != tag]
    save_tasks(tasks)
    return RedirectResponse("/", status_code=302)


@app.get("/tasks")
async def get_tasks():
    return load_tasks()
