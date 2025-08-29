from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from task import Task
from taskManager import TaskManager
from UserManager import UserManager
from datetime import datetime
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "dev_key"))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

USER_FILE = "data/users.json"

def get_user_manager():
    um = UserManager()
    um.load(USER_FILE)
    return um

def save_user_manager(um):
    um.save(USER_FILE)

def get_task_file(user: str):
    os.makedirs("data", exist_ok=True)
    return f"data/{user}_tasks.json"

def get_task_manager(user: str):
    tm = TaskManager()
    tm.load(get_task_file(user))
    return tm

def save_task_manager(user: str, tm: TaskManager):
    tm.save(get_task_file(user))

# -------------------- Routes --------------------

@app.get("/login")
async def login_form():
    return HTMLResponse("""
        <head>
          <link rel="stylesheet" href="/static/style.css" />
        <head>
        <h2>Login</h2>
        <form method="post" action="/login">
            <input name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <a href="/register">Register</a>
    """)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), request: Request = None):
    um = get_user_manager()
    if not um.verify_user(username, password):
        return HTMLResponse("Invalid username or password", status_code=400)

    request.session["user"] = username
    return RedirectResponse("/", status_code=302)

@app.get("/register")
async def register_form():
    return HTMLResponse("""
        <head>
          <link rel="stylesheet" href="/static/style.css" />
        <head>
        <h2>Register</h2>
        <form method="post" action="/register">
            <input name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Register</button>
        </form>
        <a href="/login">Login</a>
    """)

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    um = get_user_manager()
    try:
        um.add_user(username, password)
    except ValueError:
        return HTMLResponse("User already exists", status_code=400)
    save_user_manager(um)
    return RedirectResponse("/login", status_code=302)

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    tm = get_task_manager(user)
    tm.sort_by_priority()
    task_dicts = [task.to_dict() for task in tm.get_all_tasks()]

    now = datetime.now()
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    due_tasks, today_tasks, later_tasks = [], [], []

    for t in task_dicts:
        try:
            task_time = datetime.strptime(t["date"], "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        if task_time <= now:
            due_tasks.append(t)
        elif now < task_time <= today_end:
            today_tasks.append(t)
        else:
            later_tasks.append(t)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "due_tasks": due_tasks,
        "today_tasks": today_tasks,
        "later_tasks": later_tasks,
        "user": user
    })

@app.post("/add")
async def add_task(request: Request, tag: str = Form(...), date: str = Form(...), priority: int = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    tm = get_task_manager(user)
    tm.add_task(Task(tag=tag, date=date, priority=priority))
    save_task_manager(user, tm)
    return RedirectResponse("/", status_code=302)

@app.post("/remove")
async def remove_task(request: Request, tag: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    tm = get_task_manager(user)
    tm.remove_task(tag)
    save_task_manager(user, tm)
    return RedirectResponse("/", status_code=302)
