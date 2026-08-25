from __future__ import annotations

import socket
import subprocess
from dataclasses import dataclass

import psutil


@dataclass(slots=True)
class NetworkInfo:

    local_ip: str = ""
    gateway: str = ""
    internet: bool = False


class NetworkService:
    """
    Pobiera podstawowe informacje o sieci Windows.
    """

    def get_info(self) -> NetworkInfo:

        info = NetworkInfo()

        # ==================================================
        # ADAPTERY SIECIOWE
        # ==================================================

        try:

            interfaces = psutil.net_if_addrs()

            stats = psutil.net_if_stats()

            for interface_name, addresses in interfaces.items():

                # pomijamy interfejsy wyłączone
                if interface_name in stats:

                    if not stats[interface_name].isup:
                        continue

                for address in addresses:

                    if address.family != socket.AF_INET:
                        continue

                    ip = address.address

                    # pomijamy localhost
                    if ip.startswith("127."):
                        continue

                    # pierwsze znalezione IPv4
                    info.local_ip = ip
                    break

                if info.local_ip:
                    break

        except Exception:

            info.local_ip = ""

        # ==================================================
        # LOKALNY ADRES Z ROUTINGU SOCKET
        # ==================================================

        if not info.local_ip:

            try:

                sock = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_DGRAM,
                )

                try:

                    sock.connect(
                        ("8.8.8.8", 80)
                    )

                    local_address = (
                        sock.getsockname()[0]
                    )

                finally:

                    sock.close()

                if local_address:
                    info.local_ip = local_address

            except OSError:

                pass

        # ==================================================
        # GATEWAY WINDOWS
        # ==================================================

        try:

            result = subprocess.run(
                [
                    "route",
                    "print",
                    "-4",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=2,
                creationflags=getattr(
                    subprocess,
                    "CREATE_NO_WINDOW",
                    0,
                ),
            )

            for line in result.stdout.splitlines():

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) < 4:
                    continue

                destination = parts[0]
                mask = parts[1]
                gateway = parts[2]

                if (
                    destination == "0.0.0.0"
                    and mask == "0.0.0.0"
                    and gateway != "On-link"
                ):

                    info.gateway = gateway
                    break

        except (
            OSError,
            subprocess.SubprocessError,
        ):

            info.gateway = ""

        # ==================================================
        # INTERNET
        # ==================================================

        try:

            connection = socket.create_connection(
                ("8.8.8.8", 53),
                timeout=1,
            )

            connection.close()

            info.internet = True

        except OSError:

            info.internet = False

        return info