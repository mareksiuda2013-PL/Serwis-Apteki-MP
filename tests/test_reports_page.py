from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from models.system_report import (
    STATUS_ERROR,
    STATUS_OK,
    STATUS_WARNING,
    SystemReport,
)
from modules.reports.page import ReportsPage


def get_app() -> QApplication:
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    return app


class FakeReportService:
    def __init__(self, report: SystemReport):
        self.report = report
        self.calls = 0

    def build_report(self) -> SystemReport:
        self.calls += 1
        return self.report


def create_report() -> SystemReport:
    report = SystemReport()

    report.add(
        "Windows",
        STATUS_OK,
        "Komputer: TEST-PC; użytkownik: test",
    )

    report.add(
        "Sieć",
        STATUS_OK,
        "IP: 192.168.1.10; brama: 192.168.1.1; Internet: OK",
    )

    report.add(
        "Drukarki",
        STATUS_WARNING,
        "1 drukarka wymaga uwagi: HP",
    )

    report.add(
        "Kamsoft",
        STATUS_ERROR,
        "Brak APMAN.EXE",
    )

    return report


def test_reports_page_can_be_created():
    get_app()

    service = FakeReportService(create_report())
    page = ReportsPage(service=service)

    assert page is not None
    assert page.run_button.text() == "Wykonaj raport"
    assert page.refresh_button.text() == "Odśwież"

    page.close()


def test_run_report_builds_report():
    get_app()

    service = FakeReportService(create_report())
    page = ReportsPage(service=service)

    page._run_report()

    assert service.calls == 1
    assert page.status_value.text() == "BŁĄD"

    page.close()


def test_report_displays_all_sections():
    get_app()

    service = FakeReportService(create_report())
    page = ReportsPage(service=service)

    page._run_report()

    assert page.results_layout.count() == 5

    assert page.results_layout.itemAt(0).widget() is not None
    assert page.results_layout.itemAt(1).widget() is not None
    assert page.results_layout.itemAt(2).widget() is not None
    assert page.results_layout.itemAt(3).widget() is not None

    page.close()


def test_status_text():
    assert ReportsPage._status_text(STATUS_OK) == "OK"

    assert (
        ReportsPage._status_text(STATUS_WARNING)
        == "OSTRZEŻENIE"
    )

    assert (
        ReportsPage._status_text(STATUS_ERROR)
        == "BŁĄD"
    )