from PySide6.QtWidgets import QApplication

from modules.database.widget import DatabaseWidget


def get_app():
    return QApplication.instance() or QApplication([])


def test_database_widget_creates_expected_buttons():
    get_app()

    widget = DatabaseWidget()

    assert widget.btn_backup.text() == "💾 Backup"
    assert widget.btn_restore.text() == "♻ Restore"
    assert widget.btn_validate.text() == "✔ Validate"
    assert widget.btn_sweep.text() == "🧹 Sweep"
    assert widget.btn_rebuild.text() == "🔧 Odbudowa"


def test_database_widget_sets_minimum_height_for_all_buttons():
    get_app()

    widget = DatabaseWidget()

    buttons = [
        widget.btn_backup,
        widget.btn_restore,
        widget.btn_validate,
        widget.btn_sweep,
        widget.btn_rebuild,
    ]

    for button in buttons:
        assert button.minimumHeight() == 70


def test_database_widget_has_layout():
    get_app()

    widget = DatabaseWidget()

    assert widget.layout() is not None
    assert widget.layout().count() == 3
