
from __future__ import annotations

from unittest.mock import MagicMock, patch

from services.system.system_service import (
    SystemService,
)


# ==========================================================
# HELPERS
# ==========================================================


def create_service() -> SystemService:
    return SystemService()


# ==========================================================
# GET INFO
# ==========================================================


@patch(
    "services.system.system_service.psutil.cpu_count"
)
@patch(
    "services.system.system_service.psutil.cpu_freq"
)
@patch(
    "services.system.system_service.psutil.cpu_percent"
)
@patch(
    "services.system.system_service.psutil.boot_time"
)
@patch(
    "services.system.system_service.psutil.virtual_memory"
)
@patch(
    "services.system.system_service.platform.python_version"
)
@patch(
    "services.system.system_service.platform.machine"
)
@patch(
    "services.system.system_service.platform.version"
)
@patch(
    "services.system.system_service.platform.system"
)
@patch(
    "services.system.system_service.platform.processor"
)
@patch(
    "services.system.system_service.socket.gethostname"
)
@patch(
    "services.system.system_service.getpass.getuser"
)
@patch(
    "services.system.system_service.time.time"
)
@patch(
    "services.system.system_service.time.strftime"
)
@patch(
    "services.system.system_service.time.localtime"
)
def test_get_info_returns_system_info(
    localtime,
    strftime,
    time_now,
    getuser,
    gethostname,
    processor,
    platform_system,
    platform_version,
    platform_machine,
    python_version,
    virtual_memory,
    boot_time,
    cpu_percent,
    cpu_freq,
    cpu_count,
):

    memory = MagicMock()

    memory.total = 8 * (1024 ** 3)
    memory.used = 4 * (1024 ** 3)
    memory.percent = 50

    frequency = MagicMock()
    frequency.current = 3600.0

    gethostname.return_value = "TEST-PC"
    getuser.return_value = "marek"

    processor.return_value = "TEST CPU"

    platform_system.return_value = "Windows"
    platform_version.return_value = "10.0"
    platform_machine.return_value = "AMD64"
    python_version.return_value = "3.14.0"

    virtual_memory.return_value = memory

    boot_time.return_value = 1000.0
    time_now.return_value = 4600.0

    localtime.return_value = MagicMock()

    strftime.return_value = (
        "2026-08-25 10:00:00"
    )

    cpu_percent.return_value = 25.0

    cpu_freq.return_value = frequency

    cpu_count.side_effect = [
        8,
        16,
    ]

    service = create_service()

    result = service.get_info()

    assert result.computer_name == "TEST-PC"
    assert result.user == "marek"

    assert result.windows == "Windows"
    assert result.windows_version == "10.0"
    assert result.windows_architecture == "AMD64"

    assert result.cpu_name == "TEST CPU"
    assert result.cpu_usage == 25.0

    assert result.cpu_cores == 8
    assert result.cpu_threads == 16
    assert result.cpu_frequency_mhz == 3600.0

    assert result.ram_total_gb == 8.0
    assert result.ram_used_gb == 4.0
    assert result.ram_percent == 50

    assert result.boot_time == (
        "2026-08-25 10:00:00"
    )

    assert result.python_version == "3.14.0"


# ==========================================================
# CPU NAME FALLBACK
# ==========================================================


@patch(
    "services.system.system_service.platform.processor"
)
@patch(
    "services.system.system_service.psutil.virtual_memory"
)
@patch(
    "services.system.system_service.psutil.cpu_freq"
)
@patch(
    "services.system.system_service.psutil.cpu_percent"
)
@patch(
    "services.system.system_service.psutil.cpu_count"
)
@patch(
    "services.system.system_service.psutil.boot_time",
    return_value=1000.0,
)
@patch(
    "services.system.system_service.time.time",
    return_value=4600.0,
)
@patch(
    "services.system.system_service.time.localtime"
)
@patch(
    "services.system.system_service.time.strftime",
    return_value="2026-08-25 10:00:00",
)
@patch(
    "services.system.system_service.platform.machine",
    return_value="AMD64",
)
@patch(
    "services.system.system_service.platform.system",
    return_value="Windows",
)
@patch(
    "services.system.system_service.platform.version",
    return_value="10.0",
)
@patch(
    "services.system.system_service.platform.python_version",
    return_value="3.14.0",
)
@patch(
    "services.system.system_service.socket.gethostname",
    return_value="TEST-PC",
)
@patch(
    "services.system.system_service.getpass.getuser",
    return_value="marek",
)
def test_get_info_uses_cpu_fallback(
    getuser,
    gethostname,
    python_version,
    platform_version,
    platform_system,
    platform_machine,
    strftime,
    localtime,
    time_now,
    boot_time,
    cpu_count,
    cpu_percent,
    cpu_freq,
    virtual_memory,
    processor,
):

    memory = MagicMock(
        total=8 * (1024 ** 3),
        used=4 * (1024 ** 3),
        percent=50,
    )

    virtual_memory.return_value = memory

    cpu_freq.return_value = None
    cpu_percent.return_value = 10.0

    cpu_count.side_effect = [
        4,
        8,
    ]

    processor.return_value = ""

    service = create_service()

    result = service.get_info()

    assert result.cpu_name == "Nieznany"
    assert result.cpu_frequency_mhz == 0.0


# ==========================================================
# UPTIME
# ==========================================================


def test_format_uptime_zero():

    result = (
        SystemService._format_uptime(
            0
        )
    )

    assert result == (
        "0 dni, 00:00"
    )


def test_format_uptime_minutes():

    result = (
        SystemService._format_uptime(
            125 * 60
        )
    )

    assert result == (
        "0 dni, 02:05"
    )


def test_format_uptime_hours():

    result = (
        SystemService._format_uptime(
            2 * 3600
            + 15 * 60
        )
    )

    assert result == (
        "0 dni, 02:15"
    )


def test_format_uptime_days():

    result = (
        SystemService._format_uptime(
            2 * 86400
            + 3 * 3600
            + 7 * 60
        )
    )

    assert result == (
        "2 dni, 03:07"
    )


# ==========================================================
# CPU COUNTS
# ==========================================================


@patch(
    "services.system.system_service.psutil.cpu_count"
)
@patch(
    "services.system.system_service.psutil.virtual_memory"
)
@patch(
    "services.system.system_service.psutil.cpu_freq"
)
@patch(
    "services.system.system_service.psutil.cpu_percent"
)
@patch(
    "services.system.system_service.psutil.boot_time",
    return_value=0,
)
@patch(
    "services.system.system_service.time.time",
    return_value=0,
)
@patch(
    "services.system.system_service.time.localtime"
)
@patch(
    "services.system.system_service.time.strftime",
    return_value="START",
)
@patch(
    "services.system.system_service.platform.processor",
    return_value="CPU",
)
@patch(
    "services.system.system_service.platform.system",
    return_value="Windows",
)
@patch(
    "services.system.system_service.platform.version",
    return_value="VERSION",
)
@patch(
    "services.system.system_service.platform.machine",
    return_value="AMD64",
)
@patch(
    "services.system.system_service.platform.python_version",
    return_value="3.14",
)
@patch(
    "services.system.system_service.socket.gethostname",
    return_value="PC",
)
@patch(
    "services.system.system_service.getpass.getuser",
    return_value="USER",
)
def test_get_info_uses_cpu_core_counts(
    getuser,
    gethostname,
    python_version,
    machine,
    version,
    system,
    processor,
    strftime,
    localtime,
    time_now,
    boot_time,
    cpu_percent,
    cpu_freq,
    virtual_memory,
    cpu_count,
):

    virtual_memory.return_value = MagicMock(
        total=1,
        used=1,
        percent=1,
    )

    cpu_percent.return_value = 1.0
    cpu_freq.return_value = None

    cpu_count.side_effect = [
        6,
        12,
    ]

    service = create_service()

    result = service.get_info()

    assert result.cpu_cores == 6
    assert result.cpu_threads == 12


# ==========================================================
# CPU COUNT FALLBACK
# ==========================================================


@patch(
    "services.system.system_service.psutil.cpu_count",
    return_value=None,
)
@patch(
    "services.system.system_service.psutil.virtual_memory"
)
@patch(
    "services.system.system_service.psutil.cpu_freq",
    return_value=None,
)
@patch(
    "services.system.system_service.psutil.cpu_percent",
    return_value=0.0,
)
@patch(
    "services.system.system_service.psutil.boot_time",
    return_value=0,
)
@patch(
    "services.system.system_service.time.time",
    return_value=0,
)
@patch(
    "services.system.system_service.time.localtime"
)
@patch(
    "services.system.system_service.time.strftime",
    return_value="START",
)
@patch(
    "services.system.system_service.platform.processor",
    return_value="CPU",
)
@patch(
    "services.system.system_service.platform.system",
    return_value="Windows",
)
@patch(
    "services.system.system_service.platform.version",
    return_value="VERSION",
)
@patch(
    "services.system.system_service.platform.machine",
    return_value="AMD64",
)
@patch(
    "services.system.system_service.platform.python_version",
    return_value="3.14",
)
@patch(
    "services.system.system_service.socket.gethostname",
    return_value="PC",
)
@patch(
    "services.system.system_service.getpass.getuser",
    return_value="USER",
)
def test_get_info_uses_zero_when_cpu_count_unavailable(
    getuser,
    hostname,
    python_version,
    machine,
    version,
    system,
    processor,
    strftime,
    localtime,
    time_now,
    boot_time,
    cpu_percent,
    cpu_freq,
    virtual_memory,
    cpu_count,
):

    virtual_memory.return_value = MagicMock(
        total=1,
        used=1,
        percent=1,
    )

    service = create_service()

    result = service.get_info()

    assert result.cpu_cores == 0
    assert result.cpu_threads == 0