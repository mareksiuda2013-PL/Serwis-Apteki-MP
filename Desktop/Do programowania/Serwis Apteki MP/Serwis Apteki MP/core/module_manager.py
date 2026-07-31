from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtWidgets import QWidget

from modules.dashboard import DashboardPage
from modules.firebird.page import FirebirdPage
from gui.page import Page


@dataclass(slots=True)
class Module:
    """
    Opis pojedynczego modułu aplikacji.
    """

    id: str
    name: str
    icon: str
    widget: QWidget


class ModuleManager:

    def __init__(self) -> None:

        self._modules: list[Module] = []

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    @property
    def modules(self) -> list[Module]:
        return self._modules

    def load(self) -> None:
        """
        Ładuje wszystkie dostępne moduły.
        """

        self._modules.clear()

        self.register(
            Module(
                id="dashboard",
                name="Dashboard",
                icon="🏠",
                widget=DashboardPage(),
            )
        )

        self.register(
            Module(
                id="firebird",
                name="Firebird",
                icon="🗄",
                widget=FirebirdPage(),
            )
        )

        self.register(
            Module(
                id="kamsoft",
                name="Kamsoft",
                icon="💊",
                widget=Page("Kamsoft"),
            )
        )

        self.register(
            Module(
                id="network",
                name="Sieć",
                icon="🌐",
                widget=Page("Sieć"),
            )
        )

        self.register(
            Module(
                id="printers",
                name="Drukarki",
                icon="🖨",
                widget=Page("Drukarki"),
            )
        )

        self.register(
            Module(
                id="windows",
                name="Windows",
                icon="🪟",
                widget=Page("Windows"),
            )
        )

        self.register(
            Module(
                id="reports",
                name="Raporty",
                icon="📊",
                widget=Page("Raporty"),
            )
        )

        self.register(
            Module(
                id="settings",
                name="Ustawienia",
                icon="⚙",
                widget=Page("Ustawienia"),
            )
        )

    def register(self, module: Module) -> None:

        if self.exists(module.id):
            raise ValueError(
                f"Moduł '{module.id}' jest już zarejestrowany."
            )

        self._modules.append(module)

    def exists(self, module_id: str) -> bool:

        return any(
            module.id == module_id
            for module in self._modules
        )

    def get(self, module_id: str) -> Optional[Module]:

        for module in self._modules:

            if module.id == module_id:
                return module

        return None

    def names(self) -> list[str]:

        return [
            module.name
            for module in self._modules
        ]

    def widgets(self) -> list[QWidget]:

        return [
            module.widget
            for module in self._modules
        ]

    def count(self) -> int:

        return len(self._modules)