from __future__ import annotations

from models import FirebirdInfo

from .config_service import ConfigService
from .installation_service import InstallationService
from .service_service import ServiceService
from .version_service import VersionService


class FirebirdService:

    def __init__(self):

        self.installation = InstallationService()
        self.service = ServiceService()
        self.version = VersionService()
        self.config = ConfigService()

    def get_info(self) -> FirebirdInfo:

        info = FirebirdInfo()

        fb = self.installation.first_installation()

        if fb is None:
            return info

        info.installed = True
        info.exists = True

        info.install_path = fb.install_path
        info.bin_path = fb.bin_path

        info.service_name = fb.service_name
        info.service_status = self.service.status(
            fb.service_name
        )

        #
        # wersja
        #

        version = self.version.get_version(
            fb.bin_path
        )

        if version:
            info.version = version
        else:
            info.version = fb.version

        #
        # firebird.conf
        #

        info.firebird_conf = (
            fb.install_path / "firebird.conf"
        )

        config = self.config.load(
            info.firebird_conf
        )

        info.port = config.remote_service_port

        #
        # pliki
        #

        info.gbak_path = fb.bin_path / "gbak.exe"
        info.gfix_path = fb.bin_path / "gfix.exe"
        info.isql_path = fb.bin_path / "isql.exe"

        info.fbclient_path = (
            fb.install_path / "fbclient.dll"
        )

        info.gbak_exists = info.gbak_path.exists()
        info.gfix_exists = info.gfix_path.exists()
        info.isql_exists = info.isql_path.exists()
        info.fbclient_exists = (
            info.fbclient_path.exists()
        )

        info.firebird_conf_exists = (
            info.firebird_conf.exists()
        )

        return info