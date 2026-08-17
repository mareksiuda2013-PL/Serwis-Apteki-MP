from __future__ import annotations

import getpass
import platform
import socket
import time

import psutil

from models.system_info import SystemInfo


class SystemService:

    def get_info(self) -> SystemInfo:

        memory = psutil.virtual_memory()

        cpu_name = platform.processor()

        if not cpu_name:
            cpu_name = "Nieznany"

        uptime_seconds = (
            time.time() - psutil.boot_time()
        )

        return SystemInfo(
            computer_name=socket.gethostname(),

            user=getpass.getuser(),

            windows=platform.system(),

            windows_version=platform.version(),

            cpu_name=cpu_name,

            cpu_usage=psutil.cpu_percent(
                interval=None
            ),

            ram_total_gb=(
                memory.total / (1024 ** 3)
            ),

            ram_used_gb=(
                memory.used / (1024 ** 3)
            ),

            ram_percent=int(
                memory.percent
            ),

            uptime=self._format_uptime(
                uptime_seconds
            ),
        )

    # ======================================================
    # UPTIME
    # ======================================================

    @staticmethod
    def _format_uptime(
        seconds: float,
    ) -> str:

        seconds = int(seconds)

        days, seconds = divmod(
            seconds,
            86400,
        )

        hours, seconds = divmod(
            seconds,
            3600,
        )

        minutes, _ = divmod(
            seconds,
            60,
        )

        if days == 1:
            days_text = "1 dzień"
        else:
            days_text = f"{days} dni"

        return (
            f"{days_text}, "
            f"{hours} godz., "
            f"{minutes} min."
        )