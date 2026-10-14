from __future__ import annotations

from models.system_report import (
    STATUS_ERROR,
    STATUS_OK,
    STATUS_WARNING,
    ReportItem,
    SystemReport,
)


def test_report_item_defaults():
    item = ReportItem(name="Sieć")

    assert item.name == "Sieć"
    assert item.status == STATUS_OK
    assert item.message == ""


def test_report_item_values():
    item = ReportItem(
        name="Drukarki",
        status=STATUS_WARNING,
        message="Jedna drukarka jest offline.",
    )

    assert item.name == "Drukarki"
    assert item.status == STATUS_WARNING
    assert item.message == "Jedna drukarka jest offline."


def test_system_report_defaults_to_ok():
    report = SystemReport()

    assert report.items == []
    assert report.status == STATUS_OK
    assert report.has_errors is False
    assert report.has_warnings is False


def test_system_report_adds_item():
    report = SystemReport()

    item = report.add(
        "Sieć",
        STATUS_OK,
        "Połączenie działa.",
    )

    assert len(report.items) == 1
    assert item.name == "Sieć"
    assert item.status == STATUS_OK
    assert item.message == "Połączenie działa."


def test_system_report_is_warning_when_item_is_warning():
    report = SystemReport()

    report.add("Firebird", STATUS_OK)
    report.add(
        "Drukarki",
        STATUS_WARNING,
        "Drukarka offline.",
    )

    assert report.status == STATUS_WARNING
    assert report.has_warnings is True
    assert report.has_errors is False


def test_system_report_is_error_when_item_is_error():
    report = SystemReport()

    report.add("Firebird", STATUS_OK)
    report.add(
        "Sieć",
        STATUS_ERROR,
        "Brak połączenia.",
    )

    assert report.status == STATUS_ERROR
    assert report.has_errors is True
    assert report.has_warnings is False


def test_error_has_priority_over_warning():
    report = SystemReport()

    report.add(
        "Drukarki",
        STATUS_WARNING,
        "Drukarka offline.",
    )
    report.add(
        "Firebird",
        STATUS_ERROR,
        "Błąd bazy.",
    )

    assert report.status == STATUS_ERROR


def test_warning_has_priority_over_ok():
    report = SystemReport()

    report.add("Firebird", STATUS_OK)
    report.add(
        "Kamsoft",
        STATUS_WARNING,
        "Brak APMAN.",
    )
    report.add("Sieć", STATUS_OK)

    assert report.status == STATUS_WARNING