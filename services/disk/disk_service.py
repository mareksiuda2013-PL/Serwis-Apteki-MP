from __future__ import annotations

import shutil

from models.disk_info import DiskInfo


class DiskService:

    def get_disks(self) -> list[DiskInfo]:

        disks: list[DiskInfo] = []

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":

            drive = f"{letter}:\\"

            try:

                total, used, free = (
                    shutil.disk_usage(drive)
                )

            except OSError:

                continue

            total_gb = (
                total / (1024 ** 3)
            )

            used_gb = (
                used / (1024 ** 3)
            )

            free_gb = (
                free / (1024 ** 3)
            )

            percent = 0

            if total > 0:

                percent = int(
                    (used / total) * 100
                )

            disks.append(
                DiskInfo(
                    drive=f"{letter}:",
                    total_gb=total_gb,
                    used_gb=used_gb,
                    free_gb=free_gb,
                    percent=percent,
                )
            )

        return disks