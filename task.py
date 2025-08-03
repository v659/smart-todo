from datetime import datetime, timedelta


class Task:
    def __init__(self, tag, date, priority):
        self.tag = str(tag)
        try:
            self.date = datetime.strptime(date, "%Y-%m-%d %H")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD HH format and valid")
        self.priority = priority

    def isDue(self):
        return datetime.now() >= self.date

    # === Properties ===
    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if not isinstance(value, int):
            raise ValueError("Priority must be an integer")
        self._priority = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if not isinstance(value, datetime):
            raise ValueError("Date must be a datetime object")
        self._date = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Tag must be a non-empty string")
        self._tag = value.strip()

    # === Utility methods ===
    @staticmethod
    def getCurrentDate():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def parseDate(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    # === Debug / display ===
    def __repr__(self):
        return f"Task(tag='{self.tag}', date='{self.date.strftime('%Y-%m-%d %H:%M:%S')}', priority={self.priority})"




