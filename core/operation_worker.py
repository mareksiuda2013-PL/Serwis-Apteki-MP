from __future__ import annotations

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)


class OperationWorker(QObject):

    finished = Signal(object)
    error = Signal(str)

    def __init__(
        self,
        function,
    ):

        super().__init__()

        self.function = function

    @Slot()
    def run(self):

        try:

            result = self.function()

            self.finished.emit(
                result
            )

        except Exception as exc:

            self.error.emit(
                str(exc)
            )