from datetime import datetime

class Task:
    def __init__(self, tag: str, date: str, priority: int):
        if "T" in date:
            try:
                # Convert from input like 2025-08-05T15:42 to 2025-08-05 15:42
                date = datetime.strptime(date, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M")
            except ValueError:
                print("wrong date type", date)
                pass

        self.tag = tag
        self.date = date
        self.priority = priority

    def is_due(self):
        try:
            task_time = datetime.strptime(self.date, "%Y-%m-%d %H:%M")
            return datetime.now() >= task_time
        except ValueError:
            return False

    def to_dict(self):
        return {
            "tag": self.tag,
            "date": self.date,
            "priority": self.priority,
            "is_due": self.is_due()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(tag=data["tag"], date=data["date"], priority=data["priority"])
