from pathlib import Path
from datetime import datetime


class Logger:

    def __init__(self):

        Path("logs").mkdir(exist_ok=True)

        self.file = Path("logs") / f"{datetime.now():%Y-%m-%d}.log"

        self.callback = None

    def set_callback(self, callback):

        self.callback = callback

    def write(self, level, message):

        now = datetime.now().strftime("%H:%M:%S")

        line = f"[{now}] [{level}] {message}"

        with open(self.file, "a", encoding="utf8") as f:
            f.write(line + "\n")

        if self.callback:
            self.callback(line)

    def info(self, message):
        self.write("INFO", message)

    def success(self, message):
        self.write("SUCCESS", message)

    def warning(self, message):
        self.write("WARNING", message)

    def error(self, message):
        self.write("ERROR", message)


logger = Logger()