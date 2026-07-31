from services.system import SystemService


class DashboardController:

    def __init__(self):
        self.system_service = SystemService()

    def system_info(self):
        return self.system_service.get_info()