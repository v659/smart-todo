from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
import json
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="ftzkaW9Ck2QCwsV119KFhQ9eSv4c92ZL")
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


def get_user_file(user: str):
    os.makedirs("data", exist_ok=True)
    return f"data/{user}.json"

def load_user_tasks(user: str):
    try:
        with open(get_user_file(user), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_user_tasks(user: str, tasks):
    with open(get_user_file(user), "w") as f:
        json.dump(tasks, f, indent=2)
@app.get("/")
async def homepage(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    tasks = load_user_tasks(user)
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks, "user": user})



@app.post("/add")
async def add_task(request: Request, tag: str = Form(...), date: str = Form(...), priority: int = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    tasks = load_user_tasks(user)
    task = Task(tag=tag, date=date, priority=priority)
    tasks.append(task.dict())
    save_user_tasks(user, tasks)
    return RedirectResponse("/", status_code=302)



@app.post("/remove")
async def remove_task(request: Request, tag: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    tasks = load_user_tasks(user)
    tasks = [t for t in tasks if t["tag"] != tag]
    save_user_tasks(user, tasks)
    return RedirectResponse("/", status_code=302)


@app.get("/login")
async def login_form():
    return HTMLResponse("""
        <h2>Login</h2>
        <form method="post" action="/login">
            <input name="username" placeholder="Enter your username" required>
            <button type="submit">Login</button>
        </form>
    """)

@app.post("/login")
async def login(username: str = Form(...), request: Request = None):
    request.session["user"] = username
    return RedirectResponse("/", status_code=302)


@app.get("/tasks")
async def get_tasks():
    return load_tasks()
