import json
from task import Task  # assuming Task is defined in task.py


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        if not isinstance(task, Task):
            raise ValueError("Only Task objects can be added")
        self.tasks.append(task)

    def remove_task(self, tag):
        self.tasks = [task for task in self.tasks if task.tag != tag]

    def get_all_tasks(self):
        return self.tasks

    def get_due_tasks(self):
        return [task for task in self.tasks if task.isDue()]

    def sort_by_date(self):
        self.tasks.sort(key=lambda task: task.date)

    def sort_by_priority(self):
        self.tasks.sort(key=lambda task: task.priority)

    def remove_all(self):
        self.tasks.clear()

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump([
                {
                    "tag": task.tag,
                    "date": task.date.strftime("%Y-%m-%d %H"),
                    "priority": task.priority
                } for task in self.tasks
            ], f, indent=2)

    def load(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
            self.tasks = [
                Task(item["tag"], item["date"], item["priority"])
                for item in data
            ]

    def __repr__(self):
        return f"<TaskManager with {len(self.tasks)} tasks>"