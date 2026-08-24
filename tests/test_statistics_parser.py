from __future__ import annotations

from models import DatabaseStatistics
from services.firebird.statistics_parser import (
    StatisticsParser,
)


def create_parser():
    return StatisticsParser()


# ==========================================================
# EMPTY OUTPUT
# ==========================================================


def test_parse_empty_output():

    parser = create_parser()

    result = parser.parse("")

    assert isinstance(
        result,
        DatabaseStatistics,
    )

    assert result.ods == ""
    assert result.page_size == 0
    assert result.page_buffers == 0
    assert result.sweep_interval == 0
    assert result.forced_writes is False
    assert result.no_reserve is False


# ==========================================================
# PAGE SIZE
# ==========================================================


def test_parse_page_size():

    parser = create_parser()

    result = parser.parse(
        "Page size 4096"
    )

    assert result.page_size == 4096


# ==========================================================
# ODS
# ==========================================================


def test_parse_ods():

    parser = create_parser()

    result = parser.parse(
        "ODS version 12.0"
    )

    assert result.ods == "12.0"


# ==========================================================
# SWEEP INTERVAL
# ==========================================================


def test_parse_sweep_interval():

    parser = create_parser()

    result = parser.parse(
        "Sweep interval 20000"
    )

    assert result.sweep_interval == 20000


# ==========================================================
# PAGE BUFFERS
# ==========================================================


def test_parse_page_buffers():

    parser = create_parser()

    result = parser.parse(
        "Page buffers 2048"
    )

    assert result.page_buffers == 2048


# ==========================================================
# TRANSACTIONS
# ==========================================================


def test_parse_transactions():

    parser = create_parser()

    output = """
    Next transaction 1500
    Oldest transaction 1400
    Oldest active 1450
    Oldest snapshot 1430
    """

    result = parser.parse(output)

    assert result.next_transaction == 1500
    assert result.oldest_transaction == 1400
    assert result.oldest_active == 1450
    assert result.oldest_snapshot == 1430


# ==========================================================
# DIALECT
# ==========================================================


def test_parse_database_dialect():

    parser = create_parser()

    result = parser.parse(
        "Database dialect 3"
    )

    assert result.database_dialect == 3


# ==========================================================
# GENERATION
# ==========================================================


def test_parse_generation():

    parser = create_parser()

    result = parser.parse(
        "Generation 42"
    )

    assert result.generation == 42


# ==========================================================
# CREATION DATE
# ==========================================================


def test_parse_creation_date():

    parser = create_parser()

    result = parser.parse(
        "Creation date: Jan 12, 2026 10:30:00"
    )

    assert result.creation_date == (
        ": Jan 12, 2026 10:30:00"
    )


# ==========================================================
# FORCED WRITES
# ==========================================================


def test_parse_forced_writes():

    parser = create_parser()

    result = parser.parse(
        "Attributes force write"
    )

    assert result.forced_writes is True


# ==========================================================
# NO RESERVE
# ==========================================================


def test_parse_no_reserve():

    parser = create_parser()

    result = parser.parse(
        "Attributes no reserve"
    )

    assert result.no_reserve is True


# ==========================================================
# BOTH ATTRIBUTES
# ==========================================================


def test_parse_both_attributes():

    parser = create_parser()

    result = parser.parse(
        "Attributes force write, no reserve"
    )

    assert result.forced_writes is True
    assert result.no_reserve is True


# ==========================================================
# ATTRIBUTES CASE INSENSITIVE
# ==========================================================


def test_parse_attributes_case_insensitive():

    parser = create_parser()

    result = parser.parse(
        "Attributes FORCE WRITE, NO RESERVE"
    )

    assert result.forced_writes is True
    assert result.no_reserve is True


# ==========================================================
# UNKNOWN LINES
# ==========================================================


def test_parse_ignores_unknown_lines():

    parser = create_parser()

    output = """
    Unknown value 123
    Something else
    Page size 8192
    """

    result = parser.parse(output)

    assert result.page_size == 8192


# ==========================================================
# EMPTY LINES
# ==========================================================


def test_parse_ignores_empty_lines():

    parser = create_parser()

    output = """

    Page size 4096


    Sweep interval 20000

    """

    result = parser.parse(output)

    assert result.page_size == 4096
    assert result.sweep_interval == 20000


# ==========================================================
# COMPLETE GSTAT HEADER
# ==========================================================


def test_parse_complete_gstat_header():

    parser = create_parser()

    output = """
    Database "C:\\KSBAZA\\KS-APW\\WAPTEKA.FDB"
    Page size 4096
    ODS version 12.0
    Sweep interval 20000
    Page buffers 2048
    Next transaction 1500
    Oldest transaction 1400
    Oldest active 1450
    Oldest snapshot 1430
    Database dialect 3
    Creation date: Jan 12, 2026 10:30:00
    Attributes force write, no reserve
    Generation 42
    """

    result = parser.parse(output)

    assert isinstance(
        result,
        DatabaseStatistics,
    )

    assert result.ods == "12.0"
    assert result.page_size == 4096
    assert result.page_buffers == 2048
    assert result.sweep_interval == 20000

    assert result.next_transaction == 1500
    assert result.oldest_transaction == 1400
    assert result.oldest_active == 1450
    assert result.oldest_snapshot == 1430

    assert result.database_dialect == 3
    assert result.generation == 42

    assert result.creation_date == (
        ": Jan 12, 2026 10:30:00"
    )

    assert result.forced_writes is True
    assert result.no_reserve is True


# ==========================================================
# DIRECT INTEGER PARSER
# ==========================================================


def test_parse_int():

    parser = create_parser()

    assert parser._parse_int(
        "Page size 8192"
    ) == 8192


# ==========================================================
# DIRECT LAST VALUE PARSER
# ==========================================================


def test_parse_last_value():

    parser = create_parser()

    assert parser._parse_last_value(
        "ODS version 13.0"
    ) == "13.0"


# ==========================================================
# DIRECT ATTRIBUTES PARSER
# ==========================================================


def test_parse_attributes():

    parser = create_parser()

    stats = DatabaseStatistics()

    parser._parse_attributes(
        "Attributes force write, no reserve",
        stats,
    )

    assert stats.forced_writes is True
    assert stats.no_reserve is True


# ==========================================================
# DEFAULT ATTRIBUTES
# ==========================================================


def test_parse_attributes_without_flags():

    parser = create_parser()

    stats = DatabaseStatistics()

    parser._parse_attributes(
        "Attributes",
        stats,
    )

    assert stats.forced_writes is False
    assert stats.no_reserve is False