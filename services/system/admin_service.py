from __future__ import annotations

import ctypes


class AdminService:

    @staticmethod
    def is_admin() -> bool:
        try:
            return bool(
                ctypes.windll.shell32.IsUserAnAdmin()
            )
        except Exception:
            return False

    @classmethod
    def status(cls) -> str:
        return (
            "Administrator"
            if cls.is_admin()
            else "Standardowy użytkownik"
        )