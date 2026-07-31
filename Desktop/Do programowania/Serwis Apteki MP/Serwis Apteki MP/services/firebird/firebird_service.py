from pathlib import Path

from models import FirebirdInfo

from .installation_service import InstallationService


class FirebirdService:

    def __init__(self):

        self.installation = InstallationService()

    def get_info(self) -> FirebirdInfo:

        info = FirebirdInfo()

        fb = self.installation.first_installation()

        if fb is None:
            return info

        info.installed = True
        info.exists = True

        info.version = fb.version

        info.install_path = fb.install_path
        info.bin_path = fb.bin_path

        info.gbak_path = fb.bin_path / "gbak.exe"
        info.gfix_path = fb.bin_path / "gfix.exe"
        info.isql_path = fb.bin_path / "isql.exe"

        info.fbclient_path = fb.install_path / "fbclient.dll"

        info.firebird_conf = fb.install_path / "firebird.conf"

        info.gbak_exists = info.gbak_path.exists()
        info.gfix_exists = info.gfix_path.exists()
        info.isql_exists = info.isql_path.exists()
        info.fbclient_exists = info.fbclient_path.exists()
        info.firebird_conf_exists = info.firebird_conf.exists()

        return info