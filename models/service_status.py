from enum import Enum


class ServiceStatus(str, Enum):
    RUNNING = "Running"
    STOPPED = "Stopped"
    PAUSED = "Paused"
    NOT_INSTALLED = "Not Installed"
    UNKNOWN = "Unknown"