from __future__ import annotations

from services.firebird.statistics_parser import (
    StatisticsParser,
)


GSTAT_OUTPUT = """
Database "C:\\KSBAZA\\KS-APW\\WAPTEKA.FDB"

Page size 8192
ODS version 13.0
Oldest transaction 100
Oldest active 120
Oldest snapshot 125
Next transaction 500
Bumped transaction 0
Sequence number 0
Next attachment ID 1
Implementation ID 16
Shadow count 0
Page buffers 2048
Next header page 0
Database dialect 3
Creation date Aug 24, 2026 10:00:00

Attributes force write
Sweep interval 20000
Generation 10
"""


def test_parser_returns_database_statistics():

    parser = StatisticsParser()

    stats = parser.parse(
        GSTAT_OUTPUT
    )

    assert stats.ods == "13.0"
    assert stats.page_size == 8192
    assert stats.page_buffers == 2048
    assert stats.sweep_interval == 20000

    assert (
        stats.oldest_transaction
        == 100
    )

    assert (
        stats.oldest_active
        == 120
    )

    assert (
        stats.oldest_snapshot
        == 125
    )

    assert (
        stats.next_transaction
        == 500
    )

    assert (
        stats.database_dialect
        == 3
    )

    assert stats.generation == 10

    assert (
        stats.creation_date
        == "Aug 24, 2026 10:00:00"
    )

    assert stats.forced_writes is True
    assert stats.no_reserve is False


def test_parser_detects_no_reserve():

    parser = StatisticsParser()

    stats = parser.parse(
        """
        Page size 4096
        ODS version 13.0
        Attributes force write, no reserve
        """
    )

    assert stats.page_size == 4096
    assert stats.ods == "13.0"
    assert stats.forced_writes is True
    assert stats.no_reserve is True


def test_parser_ignores_unknown_lines():

    parser = StatisticsParser()

    stats = parser.parse(
        """
        Some unknown gstat line
        Another unknown value
        Page size 8192
        """
    )

    assert stats.page_size == 8192
    assert stats.ods == ""
    assert stats.page_buffers == 0
    assert stats.sweep_interval == 0


def test_parser_returns_empty_statistics_for_empty_output():

    parser = StatisticsParser()

    stats = parser.parse("")

    assert stats.ods == ""
    assert stats.page_size == 0
    assert stats.page_buffers == 0
    assert stats.sweep_interval == 0
    assert stats.next_transaction == 0