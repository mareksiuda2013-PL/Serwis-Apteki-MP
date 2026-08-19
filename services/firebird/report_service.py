from __future__ import annotations

from models import DatabaseStatistics
from models.database_health import DatabaseHealth
from models.report import (
    DatabaseReport,
    ReportItem,
)
from services.firebird.workflow_service import (
    WorkflowResult,
)


class ReportService:

    # ==================================================
    # DATABASE REPORT
    # ==================================================

    def generate(
        self,
        database: str,
        statistics: DatabaseStatistics,
        health: DatabaseHealth,
        recommendations=None,
    ) -> DatabaseReport:

        report = DatabaseReport(
            database=database,
            status=health.status,
            summary=health.summary,
        )

        self._add_statistics(
            report,
            statistics,
        )

        self._add_health(
            report,
            health,
        )

        self._add_recommendations(
            report,
            recommendations,
        )

        return report

    # ==================================================
    # WORKFLOW REPORT
    # ==================================================

    def generate_workflow_report(
        self,
        database: str,
        workflow: WorkflowResult,
    ) -> DatabaseReport:

        status = self._workflow_status(
            workflow
        )

        summary = self._workflow_summary(
            workflow
        )

        report = DatabaseReport(
            database=database,
            status=status,
            summary=summary,
        )

        # ==================================================
        # WORKFLOW
        # ==================================================

        for step in workflow.steps:

            report.items.append(
                ReportItem(
                    section="Workflow",
                    name=step.name,
                    status=self._normalize_status(
                        step.status
                    ),
                    value=step.status,
                    message=step.message,
                )
            )

        # ==================================================
        # BACKUP
        # ==================================================

        if workflow.backup_file:

            report.items.append(
                ReportItem(
                    section="Backup",
                    name="Plik backupu",
                    status="INFO",
                    value=workflow.backup_file,
                )
            )

        # ==================================================
        # DIAGNOSTYKA POCZĄTKOWA
        # ==================================================

        if workflow.initial_diagnostic:

            diagnostic = (
                workflow.initial_diagnostic
            )

            report.items.append(
                ReportItem(
                    section="Diagnostyka początkowa",
                    name="Status",
                    status=self._normalize_status(
                        diagnostic.status
                    ),
                    value=diagnostic.status,
                    message=diagnostic.message,
                )
            )

            self._add_diagnostic_details(
                report,
                diagnostic,
                "Diagnostyka początkowa",
            )

        # ==================================================
        # DIAGNOSTYKA KOŃCOWA
        # ==================================================

        if workflow.final_diagnostic:

            diagnostic = (
                workflow.final_diagnostic
            )

            report.items.append(
                ReportItem(
                    section="Diagnostyka końcowa",
                    name="Status",
                    status=self._normalize_status(
                        diagnostic.status
                    ),
                    value=diagnostic.status,
                    message=diagnostic.message,
                )
            )

            self._add_diagnostic_details(
                report,
                diagnostic,
                "Diagnostyka końcowa",
            )

        # ==================================================
        # REKOMENDACJE
        # ==================================================

        if workflow.recommendations:

            report.recommendations.extend(
                workflow.recommendations.recommendations
            )

        # ==================================================
        # ERROR
        # ==================================================

        if workflow.error:

            report.items.append(
                ReportItem(
                    section="Workflow",
                    name="Błąd",
                    status="ERROR",
                    value="ERROR",
                    message=workflow.error,
                )
            )

        return report

    # ==================================================
    # STATISTICS
    # ==================================================

    def _add_statistics(
        self,
        report: DatabaseReport,
        statistics: DatabaseStatistics,
    ) -> None:

        report.items.extend(
            [
                ReportItem(
                    section="Statystyki",
                    name="ODS",
                    status="INFO",
                    value=statistics.ods or "-",
                ),
                ReportItem(
                    section="Statystyki",
                    name="Page Size",
                    status="INFO",
                    value=str(
                        statistics.page_size
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Page Buffers",
                    status="INFO",
                    value=str(
                        statistics.page_buffers
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Sweep Interval",
                    status="INFO",
                    value=str(
                        statistics.sweep_interval
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Oldest Transaction",
                    status="INFO",
                    value=str(
                        statistics.oldest_transaction
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Oldest Active",
                    status="INFO",
                    value=str(
                        statistics.oldest_active
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Oldest Snapshot",
                    status="INFO",
                    value=str(
                        statistics.oldest_snapshot
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Next Transaction",
                    status="INFO",
                    value=str(
                        statistics.next_transaction
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Database Dialect",
                    status="INFO",
                    value=str(
                        statistics.database_dialect
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Generation",
                    status="INFO",
                    value=str(
                        statistics.generation
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Force Write",
                    status="INFO",
                    value=(
                        "ON"
                        if statistics.forced_writes
                        else "OFF"
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="No Reserve",
                    status="INFO",
                    value=(
                        "ON"
                        if statistics.no_reserve
                        else "OFF"
                    ),
                ),
                ReportItem(
                    section="Statystyki",
                    name="Creation Date",
                    status="INFO",
                    value=(
                        statistics.creation_date
                        or "-"
                    ),
                ),
            ]
        )

    # ==================================================
    # HEALTH CHECK
    # ==================================================

    def _add_health(
        self,
        report: DatabaseReport,
        health: DatabaseHealth,
    ) -> None:

        report.items.append(
            ReportItem(
                section="Health Check",
                name="Status",
                status=self._normalize_status(
                    health.status
                ),
                value=health.status,
                message=health.summary,
            )
        )

        for check in health.checks:

            report.items.append(
                ReportItem(
                    section="Health Check",
                    name=check.name,
                    status=self._normalize_status(
                        check.status
                    ),
                    value=check.value,
                    message=check.message,
                )
            )

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    def _add_recommendations(
        self,
        report: DatabaseReport,
        recommendations,
    ) -> None:

        if not recommendations:
            return

        if isinstance(
            recommendations,
            (list, tuple),
        ):

            report.recommendations.extend(
                str(item)
                for item in recommendations
            )

            return

        if hasattr(
            recommendations,
            "recommendations",
        ):

            report.recommendations.extend(
                str(item)
                for item in (
                    recommendations.recommendations
                )
            )

            return

        report.recommendations.append(
            str(recommendations)
        )

    # ==================================================
    # DIAGNOSTIC DETAILS
    # ==================================================

    def _add_diagnostic_details(
        self,
        report: DatabaseReport,
        diagnostic,
        section: str,
    ) -> None:

        report.items.extend(
            [
                ReportItem(
                    section=section,
                    name="Transaction Gap",
                    status="INFO",
                    value=str(
                        diagnostic.transaction_gap
                    ),
                ),
                ReportItem(
                    section=section,
                    name="Active Gap",
                    status="INFO",
                    value=str(
                        diagnostic.active_gap
                    ),
                ),
                ReportItem(
                    section=section,
                    name="Snapshot Gap",
                    status="INFO",
                    value=str(
                        diagnostic.snapshot_gap
                    ),
                ),
                ReportItem(
                    section=section,
                    name="No Reserve",
                    status="INFO",
                    value=(
                        "ON"
                        if diagnostic.no_reserve_warning
                        else "OFF"
                    ),
                ),
            ]
        )

    # ==================================================
    # WORKFLOW STATUS
    # ==================================================

    def _workflow_status(
        self,
        workflow: WorkflowResult,
    ) -> str:

        if workflow.error:
            return "ERROR"

        if (
            workflow.final_diagnostic
            and workflow.final_diagnostic.status
            == "error"
        ):
            return "ERROR"

        if (
            workflow.final_diagnostic
            and workflow.final_diagnostic.status
            == "warning"
        ):
            return "WARNING"

        if not workflow.success:
            return "ERROR"

        return "OK"

    # ==================================================
    # WORKFLOW SUMMARY
    # ==================================================

    def _workflow_summary(
        self,
        workflow: WorkflowResult,
    ) -> str:

        if workflow.error:

            return (
                f"Workflow zakończony błędem: "
                f"{workflow.error}"
            )

        if (
            workflow.final_diagnostic
            and workflow.final_diagnostic.message
        ):

            return (
                "Workflow zakończony. "
                + workflow.final_diagnostic.message
            )

        if workflow.success:

            return (
                "Workflow zakończony pomyślnie."
            )

        return (
            "Workflow nie został zakończony."
        )

    # ==================================================
    # STATUS NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_status(
        status: str,
    ) -> str:

        mapping = {
            "success": "OK",
            "SUCCESS": "OK",
            "ok": "OK",
            "OK": "OK",

            "warning": "WARNING",
            "WARNING": "WARNING",

            "error": "ERROR",
            "ERROR": "ERROR",

            "pending": "INFO",
            "PENDING": "INFO",

            "info": "INFO",
            "INFO": "INFO",

            "unknown": "INFO",
            "UNKNOWN": "INFO",
        }

        return mapping.get(
            status,
            "INFO",
        )