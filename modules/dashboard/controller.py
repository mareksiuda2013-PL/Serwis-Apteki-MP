from services.system import SystemService
from services.firebird import FirebirdService
from services.disk import DiskService
from services.network import NetworkService


class DashboardController:

    def __init__(self):

        self.system_service = SystemService()
        self.firebird_service = FirebirdService()
        self.disk_service = DiskService()
        self.network_service = NetworkService()

    # ==================================================
    # SYSTEM
    # ==================================================

    def system_info(self):

        return self.system_service.get_info()

    # ==================================================
    # FIREBIRD
    # ==================================================

    def firebird_info(self):

        return self.firebird_service.get_info()

    # ==================================================
    # DYSKI
    # ==================================================

    def disk_info(self):

        return self.disk_service.get_disks()

    # ==================================================
    # SIEĆ
    # ==================================================

    def network_info(self):

        return self.network_service.get_info()