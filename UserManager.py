import json
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager:
    def __init__(self):
        self.users = {}  # username -> hashed password

    def add_user(self, username: str, password: str):
        if username in self.users:
            raise ValueError("User already exists")
        self.users[username] = pwd_context.hash(password)

    def verify_user(self, username: str, password: str) -> bool:
        hashed = self.users.get(username)
        if not hashed:
            return False
        return pwd_context.verify(password, hashed)

    def save(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(self.users, f, indent=2)

    def load(self, filename):
        try:
            with open(filename, "r") as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
