from __future__ import annotations

from models import FirebirdInfo

from .installation_service import InstallationService


class FirebirdService:

    def __init__(self):

        self.installation = InstallationService()

    def get_info(self) -> FirebirdInfo:

        info = FirebirdInfo()

        installations = self.installation.find_installations()

        if not installations:
            return info

        fb = installations[0]

        info.installed = True

        info.version = fb.version

        info.install_path = fb.install_path

        info.bin_path = fb.bin_path

        return info