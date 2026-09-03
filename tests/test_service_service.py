from unittest.mock import Mock, patch

from services.firebird.service_service import ServiceService


def make_service():
    return ServiceService.__new__(ServiceService)


def test_run_sc_success():
    service = make_service()

    completed = Mock()
    completed.returncode = 0
    completed.stdout = "  OK  "
    completed.stderr = ""

    with patch(
        "services.firebird.service_service.subprocess.run",
        return_value=completed,
    ) as run:
        result = service._run_sc("query", "FirebirdServer")

    assert result == (True, "OK")
    run.assert_called_once_with(
        ["sc", "query", "FirebirdServer"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )


def test_run_sc_failure_uses_stderr_when_stdout_empty():
    service = make_service()

    completed = Mock()
    completed.returncode = 1
    completed.stdout = ""
    completed.stderr = "ERROR"

    with patch(
        "services.firebird.service_service.subprocess.run",
        return_value=completed,
    ):
        result = service._run_sc("query", "FirebirdServer")

    assert result == (False, "ERROR")


def test_run_sc_returns_empty_output_when_both_streams_empty():
    service = make_service()

    completed = Mock()
    completed.returncode = 0
    completed.stdout = ""
    completed.stderr = ""

    with patch(
        "services.firebird.service_service.subprocess.run",
        return_value=completed,
    ):
        result = service._run_sc("query", "FirebirdServer")

    assert result == (True, "")


def test_run_sc_handles_exception():
    service = make_service()

    with patch(
        "services.firebird.service_service.subprocess.run",
        side_effect=RuntimeError("boom"),
    ):
        result = service._run_sc("query", "FirebirdServer")

    assert result == (False, "boom")


def test_exists_returns_true_when_service_query_succeeds():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, "SERVICE_NAME: FirebirdServer"),
    ) as run_sc:
        result = service.exists("FirebirdServer")

    assert result is True
    run_sc.assert_called_once_with("query", "FirebirdServer")


def test_exists_returns_false_when_service_query_fails():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(False, "ERROR"),
    ):
        result = service.exists("FirebirdServer")

    assert result is False


def test_status_returns_not_installed_when_query_fails():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(False, "ERROR"),
    ):
        result = service.status("FirebirdServer")

    assert result == "Not Installed"


def test_status_detects_running():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, "STATE              : 4  RUNNING"),
    ):
        result = service.status("FirebirdServer")

    assert result == "Running"


def test_status_detects_stopped():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, "STATE              : 1  STOPPED"),
    ):
        result = service.status("FirebirdServer")

    assert result == "Stopped"


def test_status_detects_paused():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, "STATE              : 7  PAUSED"),
    ):
        result = service.status("FirebirdServer")

    assert result == "Paused"


def test_status_detects_stop_pending():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, "STATE              : 3  STOP_PENDING"),
    ):
        result = service.status("FirebirdServer")

    assert result == "Stop Pending"


def test_status_detects_start_pending():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, "STATE              : 2  START_PENDING"),
    ):
        result = service.status("FirebirdServer")

    assert result == "Start Pending"


def test_status_returns_unknown_for_unrecognized_state():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, "STATE              : 99  SOMETHING"),
    ):
        result = service.status("FirebirdServer")

    assert result == "Unknown"


def test_find_firebird_service_returns_matching_service():
    service = make_service()

    output = """
SERVICE_NAME: OtherService
        TYPE               : 10  WIN32_OWN_PROCESS
SERVICE_NAME: FirebirdServerDefaultInstance
        TYPE               : 10  WIN32_OWN_PROCESS
"""

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, output),
    ) as run_sc:
        result = service.find_firebird_service()

    assert result == "FirebirdServerDefaultInstance"
    run_sc.assert_called_once_with("query", "state=")


def test_find_firebird_service_is_case_insensitive():
    service = make_service()

    output = """
SERVICE_NAME: MyFireBirdService
"""

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, output),
    ):
        result = service.find_firebird_service()

    assert result == "MyFireBirdService"


def test_find_firebird_service_returns_none_when_query_fails():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(False, "ERROR"),
    ):
        result = service.find_firebird_service()

    assert result is None


def test_find_firebird_service_returns_none_for_empty_output():
    service = make_service()

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, ""),
    ):
        result = service.find_firebird_service()

    assert result is None


def test_find_firebird_service_ignores_non_service_lines():
    service = make_service()

    output = """
TYPE               : 10  WIN32_OWN_PROCESS
DISPLAY_NAME       : Firebird Server
SERVICE_NAME: PostgreSQL
"""

    with patch.object(
        service,
        "_run_sc",
        return_value=(True, output),
    ):
        result = service.find_firebird_service()

    assert result is None


def test_start_returns_true_when_already_running():
    service = make_service()

    with patch.object(
        service,
        "status",
        return_value="Running",
    ) as status, patch.object(service, "_run_sc") as run_sc:
        result = service.start("FirebirdServer")

    assert result is True
    status.assert_called_once_with("FirebirdServer")
    run_sc.assert_not_called()


def test_start_returns_false_when_start_command_fails():
    service = make_service()

    with patch.object(
        service,
        "status",
        return_value="Stopped",
    ), patch.object(
        service,
        "_run_sc",
        return_value=(False, "ERROR"),
    ) as run_sc:
        result = service.start("FirebirdServer")

    assert result is False
    run_sc.assert_called_once_with("start", "FirebirdServer")


def test_start_returns_true_when_service_becomes_running_immediately():
    service = make_service()

    with patch.object(
        service,
        "status",
        side_effect=["Stopped", "Running"],
    ) as status, patch.object(
        service,
        "_run_sc",
        return_value=(True, "START_PENDING"),
    ):
        result = service.start("FirebirdServer")

    assert result is True
    assert status.call_count == 2


def test_start_returns_true_for_immediate_start_pending():
    service = make_service()

    with patch.object(
        service,
        "status",
        side_effect=["Stopped", "Start Pending"],
    ), patch.object(
        service,
        "_run_sc",
        return_value=(True, "START_PENDING"),
    ):
        result = service.start("FirebirdServer")

    assert result is True


def test_start_returns_false_when_start_does_not_enter_pending_state():
    service = make_service()

    with patch.object(
        service,
        "status",
        side_effect=["Stopped", "Unknown", "Unknown"],
    ), patch.object(
        service,
        "_run_sc",
        return_value=(True, "OK"),
    ):
        result = service.start("FirebirdServer", timeout=0.01)

    assert result is False


def test_stop_returns_true_when_already_stopped():
    service = make_service()

    with patch.object(
        service,
        "status",
        return_value="Stopped",
    ) as status, patch.object(service, "_run_sc") as run_sc:
        result = service.stop("FirebirdServer")

    assert result is True
    status.assert_called_once_with("FirebirdServer")
    run_sc.assert_not_called()


def test_stop_returns_false_when_stop_command_fails():
    service = make_service()

    with patch.object(
        service,
        "status",
        return_value="Running",
    ), patch.object(
        service,
        "_run_sc",
        return_value=(False, "ERROR"),
    ) as run_sc:
        result = service.stop("FirebirdServer")

    assert result is False
    run_sc.assert_called_once_with("stop", "FirebirdServer")


def test_stop_returns_true_when_service_becomes_stopped_immediately():
    service = make_service()

    with patch.object(
        service,
        "status",
        side_effect=["Running", "Stopped"],
    ) as status, patch.object(
        service,
        "_run_sc",
        return_value=(True, "STOP_PENDING"),
    ):
        result = service.stop("FirebirdServer")

    assert result is True
    assert status.call_count == 2


def test_stop_returns_true_for_immediate_stop_pending():
    service = make_service()

    with patch.object(
        service,
        "status",
        side_effect=["Running", "Stop Pending"],
    ), patch.object(
        service,
        "_run_sc",
        return_value=(True, "STOP_PENDING"),
    ):
        result = service.stop("FirebirdServer")

    assert result is True


def test_stop_returns_false_when_stop_does_not_enter_pending_state():
    service = make_service()

    with patch.object(
        service,
        "status",
        side_effect=["Running", "Unknown", "Unknown"],
    ), patch.object(
        service,
        "_run_sc",
        return_value=(True, "OK"),
    ):
        result = service.stop("FirebirdServer", timeout=0.01)

    assert result is False


def test_restart_returns_false_when_stop_fails():
    service = make_service()

    with patch.object(service, "stop", return_value=False) as stop, patch.object(
        service, "start"
    ) as start:
        result = service.restart("FirebirdServer")

    assert result is False
    stop.assert_called_once_with("FirebirdServer")
    start.assert_not_called()


def test_restart_starts_service_after_successful_stop():
    service = make_service()

    with patch.object(service, "stop", return_value=True) as stop, patch.object(
        service, "start", return_value=True
    ) as start:
        result = service.restart("FirebirdServer")

    assert result is True
    stop.assert_called_once_with("FirebirdServer")
    start.assert_called_once_with("FirebirdServer")


def test_restart_returns_start_result():
    service = make_service()

    with patch.object(service, "stop", return_value=True), patch.object(
        service, "start", return_value=False
    ) as start:
        result = service.restart("FirebirdServer")

    assert result is False
    start.assert_called_once_with("FirebirdServer")