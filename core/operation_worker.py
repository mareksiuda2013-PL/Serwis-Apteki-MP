from __future__ import annotations

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)


class OperationWorker(QObject):
    """
    Wykonuje pojedynczą operację w osobnym wątku.

    Worker nie dotyka GUI.
    Zwraca tylko wynik przez sygnał.
    """

    finished = Signal(object)
    error = Signal(str)

    def __init__(
        self,
        function,
    ) -> None:

        super().__init__()

        self.function = function

    # ==================================================
    # RUN
    # ==================================================

    @Slot()
    def run(self) -> None:

        try:

            result = self.function()

            self.finished.emit(
                result
            )

        except Exception as exc:

            self.error.emit(
                str(exc)
            )