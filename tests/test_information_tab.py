from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from modules.firebird.tabs.information_tab import InformationTab


def make_info(**overrides):
    statistics = SimpleNamespace(
        page_buffers=2048,
        sweep_interval=20000,
        forced_writes=True,
        no_reserve=False,
        oldest_transaction=100,
        oldest_active=110,
        oldest_snapshot=105,
        next_transaction=120,
        generation=5,
        creation_date="2026-10-05 09:00",
    )

    data = dict(
        installed=True,
        version="Firebird 3.0.11",
        ods="13.0",
        sql_dialect=3,
        page_size=8192,
        tables=42,
        statistics=statistics,
        service_name="FirebirdServerDefaultInstance",
        service_status="RUNNING",
        install_path=r"C:\Program Files\Firebird\Firebird_3_0",
        bin_path=r"C:\Program Files\Firebird\Firebird_3_0\bin",
        port=3050,
        gbak_exists=True,
        gfix_exists=True,
        isql_exists=False,
        fbclient_exists=True,
        database_path=r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
        database_exists=True,
        database_size_gb=4.12,
    )

    data.update(overrides)
    return SimpleNamespace(**data)


def make_tab(controller):
    with patch.object(InformationTab, "__init__", return_value=None):
        tab = InformationTab.__new__(InformationTab)

    tab.controller = controller
    tab.selected_database = None

    labels = [
        "lbl_installed",
        "lbl_version",
        "lbl_ods",
        "lbl_dialect",
        "lbl_page_size",
        "lbl_tables",
        "lbl_buffers",
        "lbl_sweep",
        "lbl_forced_writes",
        "lbl_no_reserve",
        "lbl_oldest_transaction",
        "lbl_oldest_active",
        "lbl_oldest_snapshot",
        "lbl_next_transaction",
        "lbl_generation",
        "lbl_creation_date",
        "lbl_service",
        "lbl_status",
        "lbl_install",
        "lbl_bin",
        "lbl_port",
        "lbl_gbak",
        "lbl_gfix",
        "lbl_isql",
        "lbl_fbclient",
        "lbl_database",
        "lbl_db_file",
        "lbl_db_size",
        "lbl_db_date",
    ]

    for name in labels:
        setattr(tab, name, MagicMock())

    tab.refresh_button = MagicMock()
    tab.database_button = MagicMock()

    return tab


def test_refresh_populates_information():
    controller = MagicMock()
    controller.info.return_value = make_info()

    tab = make_tab(controller)

    with patch(
        "modules.firebird.tabs.information_tab.Path.stat"
    ) as stat_mock:
        stat_mock.return_value.st_mtime = 1791187200
        tab.refresh()

    controller.info.assert_called_once_with(database=None)

    tab.lbl_installed.setText.assert_called_once_with("TAK")
    tab.lbl_version.setText.assert_called_once_with("Firebird 3.0.11")
    tab.lbl_ods.setText.assert_called_once_with("13.0")
    tab.lbl_dialect.setText.assert_called_once_with("3")
    tab.lbl_page_size.setText.assert_called_once_with("8192")
    tab.lbl_tables.setText.assert_called_once_with("42")

    tab.lbl_buffers.setText.assert_called_once_with("2048")
    tab.lbl_sweep.setText.assert_called_once_with("20000")
    tab.lbl_forced_writes.setText.assert_called_once_with("TAK")
    tab.lbl_no_reserve.setText.assert_called_once_with("NIE")
    tab.lbl_oldest_transaction.setText.assert_called_once_with("100")
    tab.lbl_oldest_active.setText.assert_called_once_with("110")
    tab.lbl_oldest_snapshot.setText.assert_called_once_with("105")
    tab.lbl_next_transaction.setText.assert_called_once_with("120")
    tab.lbl_generation.setText.assert_called_once_with("5")
    tab.lbl_creation_date.setText.assert_called_once_with("2026-10-05 09:00")

    tab.lbl_service.setText.assert_called_once_with(
        "FirebirdServerDefaultInstance"
    )
    tab.lbl_status.setText.assert_called_once_with("RUNNING")

    tab.lbl_install.setText.assert_called_once_with(
        r"C:\Program Files\Firebird\Firebird_3_0"
    )
    tab.lbl_bin.setText.assert_called_once_with(
        r"C:\Program Files\Firebird\Firebird_3_0\bin"
    )
    tab.lbl_port.setText.assert_called_once_with("3050")

    tab.lbl_database.setText.assert_called_once_with("WAPTEKA.FDB")
    tab.lbl_db_file.setText.assert_called_once_with("OK")
    tab.lbl_db_size.setText.assert_called_once_with("4.12 GB")


def test_refresh_clears_statistics_when_statistics_are_missing():
    controller = MagicMock()
    controller.info.return_value = make_info(statistics=None)

    tab = make_tab(controller)

    tab.refresh()

    for label_name in [
        "lbl_buffers",
        "lbl_sweep",
        "lbl_forced_writes",
        "lbl_no_reserve",
        "lbl_oldest_transaction",
        "lbl_oldest_active",
        "lbl_oldest_snapshot",
        "lbl_next_transaction",
        "lbl_generation",
        "lbl_creation_date",
    ]:
        getattr(tab, label_name).setText.assert_called_once_with("-")


def test_refresh_handles_controller_error():
    controller = MagicMock()
    controller.info.side_effect = RuntimeError("test error")

    tab = make_tab(controller)

    tab.refresh()

    controller.info.assert_called_once_with(database=None)
    tab.lbl_installed.setText.assert_called_once_with("BŁĄD")
    tab.lbl_version.setText.assert_called_once_with("test error")


def test_select_database_sets_selected_database_and_refreshes():
    controller = MagicMock()
    tab = make_tab(controller)

    with patch(
        "modules.firebird.tabs.information_tab.QFileDialog.getOpenFileName",
        return_value=(r"C:\test\database.fdb", "Firebird (*.fdb *.gdb)"),
    ):
        with patch.object(tab, "refresh") as refresh_mock:
            tab.select_database()

    assert tab.selected_database == r"C:\test\database.fdb"
    refresh_mock.assert_called_once()


def test_select_database_does_nothing_when_cancelled():
    controller = MagicMock()
    tab = make_tab(controller)

    with patch(
        "modules.firebird.tabs.information_tab.QFileDialog.getOpenFileName",
        return_value=("", ""),
    ):
        with patch.object(tab, "refresh") as refresh_mock:
            tab.select_database()

    assert tab.selected_database is None
    refresh_mock.assert_not_called()
