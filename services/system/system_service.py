from __future__ import annotations

import getpass
import platform
import socket
import time

import psutil

from models.system_info import SystemInfo


class SystemService:

    def get_info(self) -> SystemInfo:

        # ==================================================
        # RAM
        # ==================================================

        memory = psutil.virtual_memory()

        # ==================================================
        # CPU
        # ==================================================

        cpu_name = platform.processor()

        if not cpu_name:
            cpu_name = "Nieznany"

        cpu_frequency = psutil.cpu_freq()

        if cpu_frequency is not None:
            cpu_frequency_mhz = cpu_frequency.current
        else:
            cpu_frequency_mhz = 0.0

        # ==================================================
        # UPTIME
        # ==================================================

        boot_timestamp = psutil.boot_time()

        uptime_seconds = (
            time.time() - boot_timestamp
        )

        boot_time = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(boot_timestamp),
        )

        # ==================================================
        # SYSTEM
        # ==================================================

        architecture = (
            platform.machine()
            or "Nieznana"
        )

        # ==================================================
        # CPU USAGE
        # ==================================================

        cpu_usage = psutil.cpu_percent(
            interval=None
        )

        # ==================================================
        # CPU CORES / THREADS
        # ==================================================

        cpu_cores = (
            psutil.cpu_count(
                logical=False
            )
            or 0
        )

        cpu_threads = (
            psutil.cpu_count(
                logical=True
            )
            or 0
        )

        # ==================================================
        # SYSTEM INFO
        # ==================================================

        return SystemInfo(

            # --------------------------------------------------
            # KOMPUTER
            # --------------------------------------------------

            computer_name=socket.gethostname(),

            user=getpass.getuser(),

            # --------------------------------------------------
            # WINDOWS
            # --------------------------------------------------

            windows=platform.system(),

            windows_version=platform.version(),

            windows_architecture=architecture,

            # --------------------------------------------------
            # CPU
            # --------------------------------------------------

            cpu_name=cpu_name,

            cpu_usage=cpu_usage,

            cpu_cores=cpu_cores,

            cpu_threads=cpu_threads,

            cpu_frequency_mhz=cpu_frequency_mhz,

            # --------------------------------------------------
            # RAM
            # --------------------------------------------------

            ram_total_gb=(
                memory.total / (1024 ** 3)
            ),

            ram_used_gb=(
                memory.used / (1024 ** 3)
            ),

            ram_percent=int(
                memory.percent
            ),

            # --------------------------------------------------
            # SYSTEM
            # --------------------------------------------------

            uptime=self._format_uptime(
                uptime_seconds
            ),

            boot_time=boot_time,

            # --------------------------------------------------
            # PYTHON
            # --------------------------------------------------

            python_version=(
                platform.python_version()
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

        return (
            f"{days} dni, "
            f"{hours:02d}:{minutes:02d}"
        )