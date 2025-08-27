from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
from task import Task
from taskManager import TaskManager

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="my_super_secret_key")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_user_file(user: str):
    os.makedirs("data", exist_ok=True)
    return f"data/{user}.json"

def get_user_manager(user: str):
    tm = TaskManager()
    try:
        tm.load(get_user_file(user))
    except FileNotFoundError:
        pass
    return tm

def save_user_manager(user: str, tm: TaskManager):
    tm.save(get_user_file(user))


from datetime import datetime

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    tm = get_user_manager(user)
    tm.sort_by_priority()
    task_dicts = [task.to_dict() for task in tm.get_all_tasks()]

    now = datetime.now()
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    due_tasks = []
    today_tasks = []
    later_tasks = []

    for t in task_dicts:
        # Parse date string -> datetime
        try:
            task_time = datetime.fromisoformat(t["date"])
        except ValueError:
            # If your date format is different, adjust here
            continue

        if task_time <= now:
            due_tasks.append(t)
        elif now < task_time <= today_end:
            today_tasks.append(t)
        else:
            later_tasks.append(t)

    print("DUE:", due_tasks)
    print("TODAY:", today_tasks)
    print("LATER:", later_tasks)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tasks": task_dicts,
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

    tm = get_user_manager(user)
    task = Task(tag=tag, date=date, priority=priority)
    tm.add_task(task)
    save_user_manager(user, tm)
    return RedirectResponse("/", status_code=302)


@app.post("/remove")
async def remove_task(request: Request, tag: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    tm = get_user_manager(user)
    tm.remove_task(tag)
    save_user_manager(user, tm)
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


@app.post("/logout")
async def logout_button(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


@app.get("/tasks")
async def get_tasks(request: Request):
    user = request.session.get("user")
    if not user:
        return []
    tm = get_user_manager(user)
    return [task.to_dict() for task in tm.get_all_tasks()]
