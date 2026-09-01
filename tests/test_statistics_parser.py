from __future__ import annotations

import pytest

from models import DatabaseStatistics
from services.firebird.statistics_parser import (
    StatisticsParser,
)


# ==========================================================
# HELPERS
# ==========================================================


def create_parser() -> StatisticsParser:

    return StatisticsParser()


# ==========================================================
# FULL OUTPUT
# ==========================================================


def test_parse_full_gstat_output():

    parser = create_parser()

    output = """
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

    result = parser.parse(output)

    assert isinstance(
        result,
        DatabaseStatistics,
    )

    assert result.page_size == 8192
    assert result.ods == "13.0"
    assert result.oldest_transaction == 100
    assert result.oldest_active == 120
    assert result.oldest_snapshot == 125
    assert result.next_transaction == 500
    assert result.page_buffers == 2048
    assert result.database_dialect == 3
    assert result.creation_date == (
        "Aug 24, 2026 10:00:00"
    )
    assert result.sweep_interval == 20000
    assert result.generation == 10
    assert result.forced_writes is True
    assert result.no_reserve is False


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
    assert result.oldest_transaction == 0
    assert result.oldest_active == 0
    assert result.oldest_snapshot == 0
    assert result.next_transaction == 0
    assert result.database_dialect == 0
    assert result.generation == 0
    assert result.creation_date == ""


# ==========================================================
# UNKNOWN LINES
# ==========================================================


def test_parse_ignores_unknown_lines():

    parser = create_parser()

    output = """
    Some unknown gstat line
    Another unknown value
    Page size 8192
    Unknown setting 123
    """

    result = parser.parse(output)

    assert result.page_size == 8192
    assert result.ods == ""


# ==========================================================
# WHITESPACE
# ==========================================================


def test_parse_ignores_empty_lines_and_whitespace():

    parser = create_parser()

    output = """
    
       Page size 4096
    
    
       ODS version 12.0
    
    
    """

    result = parser.parse(output)

    assert result.page_size == 4096
    assert result.ods == "12.0"


# ==========================================================
# INTEGER FIELDS
# ==========================================================


@pytest.mark.parametrize(
    "line,attribute,expected",
    [
        (
            "Page size 4096",
            "page_size",
            4096,
        ),
        (
            "Page buffers 1024",
            "page_buffers",
            1024,
        ),
        (
            "Sweep interval 10000",
            "sweep_interval",
            10000,
        ),
        (
            "Oldest transaction 50",
            "oldest_transaction",
            50,
        ),
        (
            "Oldest active 60",
            "oldest_active",
            60,
        ),
        (
            "Oldest snapshot 70",
            "oldest_snapshot",
            70,
        ),
        (
            "Next transaction 80",
            "next_transaction",
            80,
        ),
        (
            "Database dialect 3",
            "database_dialect",
            3,
        ),
        (
            "Generation 15",
            "generation",
            15,
        ),
    ],
)
def test_parse_integer_fields(
    line,
    attribute,
    expected,
):

    parser = create_parser()

    result = parser.parse(line)

    assert getattr(
        result,
        attribute,
    ) == expected


# ==========================================================
# ODS
# ==========================================================


def test_parse_ods_version():

    parser = create_parser()

    result = parser.parse(
        "ODS version 13.0"
    )

    assert result.ods == "13.0"


def test_parse_ods_version_with_extra_whitespace():

    parser = create_parser()

    result = parser.parse(
        "ODS version       13.0"
    )

    assert result.ods == "13.0"


# ==========================================================
# CREATION DATE
# ==========================================================


def test_parse_creation_date():

    parser = create_parser()

    result = parser.parse(
        "Creation date Aug 24, 2026 10:00:00"
    )

    assert result.creation_date == (
        "Aug 24, 2026 10:00:00"
    )


def test_parse_creation_date_with_whitespace():

    parser = create_parser()

    result = parser.parse(
        "Creation date    Aug 24, 2026 10:00:00"
    )

    assert result.creation_date == (
        "Aug 24, 2026 10:00:00"
    )


# ==========================================================
# ATTRIBUTES
# ==========================================================


def test_parse_force_write():

    parser = create_parser()

    result = parser.parse(
        "Attributes force write"
    )

    assert result.forced_writes is True
    assert result.no_reserve is False


def test_parse_no_reserve():

    parser = create_parser()

    result = parser.parse(
        "Attributes no reserve"
    )

    assert result.forced_writes is False
    assert result.no_reserve is True


def test_parse_force_write_and_no_reserve():

    parser = create_parser()

    result = parser.parse(
        "Attributes force write no reserve"
    )

    assert result.forced_writes is True
    assert result.no_reserve is True


def test_parse_attributes_case_insensitive():

    parser = create_parser()

    result = parser.parse(
        "Attributes FORCE WRITE NO RESERVE"
    )

    assert result.forced_writes is True
    assert result.no_reserve is True


def test_parse_attributes_without_known_flags():

    parser = create_parser()

    result = parser.parse(
        "Attributes something else"
    )

    assert result.forced_writes is False
    assert result.no_reserve is False


# ==========================================================
# STATIC HELPERS
# ==========================================================


def test_parse_int_helper():

    result = StatisticsParser._parse_int(
        "Page size 8192"
    )

    assert result == 8192


def test_parse_last_value_helper():

    result = StatisticsParser._parse_last_value(
        "ODS version 13.0"
    )

    assert result == "13.0"


# ==========================================================
# INVALID INTEGER
# ==========================================================


def test_parse_invalid_integer_raises_value_error():

    parser = create_parser()

    with pytest.raises(
        ValueError
    ):

        parser.parse(
            "Page size INVALID"
        )


# ==========================================================
# MULTIPLE ATTRIBUTE LINES
# ==========================================================


def test_parse_multiple_attribute_lines():

    parser = create_parser()

    output = """
    Attributes force write
    Attributes no reserve
    """

    result = parser.parse(output)

    assert result.forced_writes is False
    assert result.no_reserve is True