import json
from task import Task
import os

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, tag: str):
        self.tasks = [t for t in self.tasks if t.tag != tag]

    def get_all_tasks(self):
        return self.tasks

    def sort_by_priority(self):
        self.tasks.sort(key=lambda t: t.priority)

    def save(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(d) for d in data]
        except FileNotFoundError:
            self.tasks = []
