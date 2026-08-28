from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from models import FirebirdInfo
from services.firebird.firebird_service import FirebirdService
from services.firebird.discovery.installation_service import (
    FirebirdInstallation,
)


def create_installation() -> FirebirdInstallation:
    return FirebirdInstallation(
        install_path=Path(
            r"C:\Program Files\Firebird\Firebird_5_0"
        ),
        version="Firebird 5.0",
        fbclient=Path(
            r"C:\Program Files\Firebird\Firebird_5_0\fbclient.dll"
        ),
        isql=Path(
            r"C:\Program Files\Firebird\Firebird_5_0\isql.exe"
        ),
        gbak=Path(
            r"C:\Program Files\Firebird\Firebird_5_0\gbak.exe"
        ),
        gfix=Path(
            r"C:\Program Files\Firebird\Firebird_5_0\gfix.exe"
        ),
        gstat=Path(
            r"C:\Program Files\Firebird\Firebird_5_0\gstat.exe"
        ),
        firebird_conf=Path(
            r"C:\Program Files\Firebird\Firebird_5_0\firebird.conf"
        ),
    )


def create_service():

    with (
        patch(
            "services.firebird.firebird_service.Config"
        ) as config_cls,
        patch(
            "services.firebird.firebird_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.firebird_service.DatabaseService"
        ) as database_cls,
        patch(
            "services.firebird.firebird_service.ServiceService"
        ) as service_cls,
    ):

        service = FirebirdService()

        return (
            service,
            config_cls.return_value,
            installation_cls.return_value,
            database_cls.return_value,
            service_cls.return_value,
        )


# ==========================================================
# INSTALLATION
# ==========================================================


def test_get_info_returns_empty_info_when_firebird_missing():

    (
        service,
        _,
        installation_service,
        _,
        _,
    ) = create_service()

    installation_service.first_installation.return_value = None

    result = service.get_info()

    assert isinstance(
        result,
        FirebirdInfo,
    )

    assert result.installed is False
    assert result.exists is False


def test_get_info_reads_installation():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation = create_installation()

    installation_service.first_installation.return_value = (
        installation
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    result = service.get_info()

    assert result.installed is True
    assert result.exists is True

    assert result.install_path == (
        installation.install_path
    )

    assert result.bin_path == (
        installation.install_path
    )

    assert result.version == (
        installation.version
    )

    assert result.gbak_path == (
        installation.gbak
    )

    assert result.gfix_path == (
        installation.gfix
    )

    assert result.isql_path == (
        installation.isql
    )

    assert result.fbclient_path == (
        installation.fbclient
    )

    assert result.firebird_conf == (
        installation.firebird_conf
    )


def test_get_info_sets_tool_existence_flags():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation = create_installation()

    installation_service.first_installation.return_value = (
        installation
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    result = service.get_info()

    assert result.gbak_exists is True
    assert result.gfix_exists is True
    assert result.isql_exists is True
    assert result.fbclient_exists is True
    assert result.firebird_conf_exists is True


def test_get_info_handles_missing_tools():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation = create_installation()

    installation.gbak = None
    installation.gfix = None
    installation.isql = None
    installation.fbclient = None
    installation.firebird_conf = None

    installation_service.first_installation.return_value = (
        installation
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    result = service.get_info()

    assert result.gbak_exists is False
    assert result.gfix_exists is False
    assert result.isql_exists is False
    assert result.fbclient_exists is False
    assert result.firebird_conf_exists is False


# ==========================================================
# DATABASE
# ==========================================================


def test_get_info_uses_configured_database():

    (
        service,
        config,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    config.database = (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    result = service.get_info()

    assert result.database_path == (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    database.exists.assert_called_once_with(
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    database.size_gb.assert_called_once_with(
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )


def test_get_info_uses_provided_database():

    (
        service,
        config,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    config.database = (
        r"C:\configured\database.fdb"
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    database_path = (
        r"C:\test\database.fdb"
    )

    result = service.get_info(
        database=database_path
    )

    assert result.database_path == (
        database_path
    )

    database.exists.assert_called_once_with(
        database_path
    )

    database.size_gb.assert_called_once_with(
        database_path
    )


def test_get_info_reads_database_size():

    (
        service,
        config,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    config.database = (
        r"C:\test\database.fdb"
    )

    database.exists.return_value = True
    database.size_gb.return_value = 12.5

    database.tables.return_value = 42

    firebird_service.find_firebird_service.return_value = None

    with patch(
        "services.firebird.firebird_service.StatisticsService"
    ) as statistics_cls:

        statistics_cls.return_value.statistics.side_effect = (
            RuntimeError("test")
        )

        result = service.get_info()

    assert result.database_exists is True
    assert result.database_size_gb == 12.5


# ==========================================================
# STATISTICS
# ==========================================================


def test_get_info_reads_statistics_when_database_exists():

    (
        service,
        config,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    config.database = (
        r"C:\test\database.fdb"
    )

    database.exists.return_value = True
    database.size_gb.return_value = 10.0

    database.tables.return_value = 25

    firebird_service.find_firebird_service.return_value = None

    statistics = MagicMock()

    statistics.ods = "13.0"
    statistics.page_size = 8192
    statistics.database_dialect = 3
    statistics.page_buffers = 2048
    statistics.sweep_interval = 20000
    statistics.forced_writes = True

    with patch(
        "services.firebird.firebird_service.StatisticsService"
    ) as statistics_cls:

        statistics_cls.return_value.statistics.return_value = (
            statistics
        )

        result = service.get_info()

    assert result.statistics is statistics

    assert result.ods == "13.0"
    assert result.page_size == 8192
    assert result.sql_dialect == 3

    assert result.tables == 25


def test_get_info_does_not_read_statistics_when_database_missing():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    with patch(
        "services.firebird.firebird_service.StatisticsService"
    ) as statistics_cls:

        result = service.get_info()

    statistics_cls.assert_not_called()

    assert result.statistics is None


def test_get_info_handles_statistics_failure():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    database.exists.return_value = True
    database.size_gb.return_value = 5.0
    database.tables.return_value = 10

    firebird_service.find_firebird_service.return_value = None

    with patch(
        "services.firebird.firebird_service.StatisticsService"
    ) as statistics_cls:

        statistics_cls.return_value.statistics.side_effect = (
            RuntimeError("GSTAT error")
        )

        result = service.get_info()

    assert result.statistics is None
    assert result.ods == ""
    assert result.page_size == 0
    assert result.sql_dialect == 0


# ==========================================================
# TABLES
# ==========================================================


def test_get_info_reads_table_count():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    database.exists.return_value = True
    database.size_gb.return_value = 8.0
    database.tables.return_value = 123

    firebird_service.find_firebird_service.return_value = None

    with patch(
        "services.firebird.firebird_service.StatisticsService"
    ) as statistics_cls:

        statistics_cls.return_value.statistics.side_effect = (
            RuntimeError("test")
        )

        result = service.get_info()

    assert result.tables == 123

    database.tables.assert_called_once_with()


def test_get_info_handles_table_failure():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    database.exists.return_value = True
    database.size_gb.return_value = 8.0

    database.tables.side_effect = (
        RuntimeError("table error")
    )

    firebird_service.find_firebird_service.return_value = None

    with patch(
        "services.firebird.firebird_service.StatisticsService"
    ) as statistics_cls:

        statistics_cls.return_value.statistics.side_effect = (
            RuntimeError("statistics error")
        )

        result = service.get_info()

    assert result.tables == 0


# ==========================================================
# FIREBIRD SERVICE
# ==========================================================


def test_get_info_reads_firebird_service():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    firebird_service.status.return_value = "Running"

    result = service.get_info()

    assert result.service_name == (
        "FirebirdServerDefaultInstance"
    )

    assert result.service_status == "Running"

    firebird_service.status.assert_called_once_with(
        "FirebirdServerDefaultInstance"
    )


def test_get_info_handles_missing_firebird_service():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    result = service.get_info()

    assert result.service_name == ""
    assert result.service_status == ""

    firebird_service.status.assert_not_called()


# ==========================================================
# VERSION
# ==========================================================


def test_get_info_uses_dash_for_missing_version():

    (
        service,
        _,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation = create_installation()
    installation.version = ""

    installation_service.first_installation.return_value = (
        installation
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    result = service.get_info()

    assert result.version == "-"


# ==========================================================
# DATABASE PATH PRIORITY
# ==========================================================


def test_provided_database_has_priority_over_configured_database():

    (
        service,
        config,
        installation_service,
        database,
        firebird_service,
    ) = create_service()

    installation_service.first_installation.return_value = (
        create_installation()
    )

    config.database = (
        r"C:\configured\database.fdb"
    )

    database.exists.return_value = False
    database.size_gb.return_value = 0.0

    firebird_service.find_firebird_service.return_value = None

    provided_database = (
        r"C:\provided\database.fdb"
    )

    result = service.get_info(
        database=provided_database
    )

    assert result.database_path == (
        provided_database
    )

    database.exists.assert_called_once_with(
        provided_database
    )

    database.size_gb.assert_called_once_with(
        provided_database
    )