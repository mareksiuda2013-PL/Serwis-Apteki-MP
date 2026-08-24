from __future__ import annotations

from unittest.mock import MagicMock, patch

from services.firebird.statistics_service import (
    StatisticsService,
)


GSTAT_OUTPUT = """
Database "C:\\KSBAZA\\KS-APW\\WAPTEKA.FDB"

Page size 8192
ODS version 13.0
Oldest transaction 100
Oldest active 120
Oldest snapshot 125
Next transaction 500
Page buffers 2048
Database dialect 3
Creation date Aug 24, 2026 10:00:00
Attributes force write
Sweep interval 20000
Generation 10
"""


def create_service() -> StatisticsService:

    installation = MagicMock()

    installation.gstat = (
        "C:/Firebird/bin/gstat.exe"
    )

    with patch(
        "services.firebird.statistics_service.BaseFirebirdService.__init__",
        return_value=None,
    ):

        service = StatisticsService.__new__(
            StatisticsService
        )

    service.installation = installation
    service.gstat = installation.gstat
    service.database = "C:/database/test.fdb"

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.runner = MagicMock()

    # StatisticsService.__init__ nie został wywołany,
    # dlatego parser tworzymy ręcznie.
    from services.firebird.statistics_parser import (
        StatisticsParser,
    )

    service.parser = StatisticsParser()

    return service


# ============================================================
# HEADER
# ============================================================


def test_header_builds_gstat_command():

    service = create_service()

    process_result = MagicMock()

    process_result.success = True
    process_result.stdout = GSTAT_OUTPUT
    process_result.stderr = ""
    process_result.return_code = 0

    service.runner.run.return_value = (
        process_result
    )

    result = service.header()

    assert result is process_result

    service.runner.run.assert_called_once()

    command = (
        service.runner.run.call_args.args[0]
    )

    assert command[0] == (
        "C:/Firebird/bin/gstat.exe"
    )

    assert "-h" in command
    assert "C:/database/test.fdb" in command
    assert "-user" in command
    assert "SYSDBA" in command
    assert "-password" in command
    assert "masterkey" in command


# ============================================================
# STATISTICS
# ============================================================


def test_statistics_uses_parser():

    service = create_service()

    process_result = MagicMock()

    process_result.success = True
    process_result.stdout = GSTAT_OUTPUT
    process_result.stderr = ""

    service.header = MagicMock(
        return_value=process_result
    )

    service.parser = MagicMock()

    expected = MagicMock()

    service.parser.parse.return_value = (
        expected
    )

    result = service.statistics()

    assert result is expected

    service.parser.parse.assert_called_once_with(
        GSTAT_OUTPUT
    )


# ============================================================
# GSTAT ERROR
# ============================================================


def test_statistics_raises_when_gstat_fails():

    service = create_service()

    process_result = MagicMock()

    process_result.success = False
    process_result.stdout = ""
    process_result.stderr = (
        "GSTAT ERROR"
    )

    service.header = MagicMock(
        return_value=process_result
    )

    try:

        service.statistics()

    except RuntimeError as exc:

        assert str(exc) == (
            "GSTAT ERROR"
        )

    else:

        raise AssertionError(
            "Oczekiwano RuntimeError."
        )