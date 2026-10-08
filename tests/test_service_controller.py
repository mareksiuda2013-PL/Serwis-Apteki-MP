from unittest.mock import MagicMock, patch

from services.firebird.service_controller import ServiceController


def test_run_sc_returns_true_and_stdout():
    controller = ServiceController()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SERVICE OK",
            stderr="",
        )

        success, output = controller._run_sc(
            "query",
            "FirebirdServerDefaultInstance",
        )

    assert success is True
    assert output == "SERVICE OK"

    mock_run.assert_called_once_with(
        ["sc", "query", "FirebirdServerDefaultInstance"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )


def test_run_sc_uses_stderr_when_stdout_empty():
    controller = ServiceController()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="ERROR",
        )

        success, output = controller._run_sc("query", "TestService")

    assert success is False
    assert output == "ERROR"


def test_run_sc_returns_empty_output_when_both_streams_empty():
    controller = ServiceController()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )

        success, output = controller._run_sc("query", "TestService")

    assert success is True
    assert output == ""


def test_run_sc_returns_exception_message():
    controller = ServiceController()

    with patch("subprocess.run", side_effect=RuntimeError("boom")):
        success, output = controller._run_sc("query", "TestService")

    assert success is False
    assert output == "boom"


def test_exists_returns_true_when_service_exists():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, "SERVICE_NAME: TestService"),
    ):
        assert controller.exists("TestService") is True


def test_exists_returns_false_when_service_does_not_exist():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(False, "service not found"),
    ):
        assert controller.exists("TestService") is False


def test_status_returns_not_installed_when_query_fails():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(False, ""),
    ):
        assert controller.status("TestService") == "Not Installed"


def test_status_returns_running():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, "STATE : 4 RUNNING"),
    ):
        assert controller.status("TestService") == "Running"


def test_status_returns_stopped():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, "STATE : 1 STOPPED"),
    ):
        assert controller.status("TestService") == "Stopped"


def test_status_returns_paused():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, "STATE : 7 PAUSED"),
    ):
        assert controller.status("TestService") == "Paused"


def test_status_returns_stop_pending():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, "STATE : 3 STOP_PENDING"),
    ):
        assert controller.status("TestService") == "Stop Pending"


def test_status_returns_start_pending():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, "STATE : 2 START_PENDING"),
    ):
        assert controller.status("TestService") == "Start Pending"


def test_status_returns_unknown_for_unrecognized_state():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, "STATE : 99 SOMETHING"),
    ):
        assert controller.status("TestService") == "Unknown"


def test_find_firebird_service_returns_matching_service():
    controller = ServiceController()

    output = """
SERVICE_NAME: SomeService
SERVICE_NAME: FirebirdServerDefaultInstance
SERVICE_NAME: AnotherService
"""

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, output),
    ):
        assert (
            controller.find_firebird_service()
            == "FirebirdServerDefaultInstance"
        )


def test_find_firebird_service_is_case_insensitive():
    controller = ServiceController()

    output = """
SERVICE_NAME: OtherService
SERVICE_NAME: firebirdserverdefaultinstance
"""

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, output),
    ):
        assert (
            controller.find_firebird_service()
            == "firebirdserverdefaultinstance"
        )


def test_find_firebird_service_returns_none_when_query_fails():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(False, "error"),
    ):
        assert controller.find_firebird_service() is None


def test_find_firebird_service_returns_none_for_empty_output():
    controller = ServiceController()

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, ""),
    ):
        assert controller.find_firebird_service() is None


def test_find_firebird_service_ignores_non_service_lines():
    controller = ServiceController()

    output = """
STATE              : 4 RUNNING
DISPLAY_NAME       : Firebird Server
SERVICE_TYPE       : 10 WIN32_OWN_PROCESS
"""

    with patch.object(
        controller,
        "_run_sc",
        return_value=(True, output),
    ):
        assert controller.find_firebird_service() is None


def test_start_returns_true_when_already_running():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        return_value="Running",
    ) as mock_status:
        assert controller.start("TestService") is True

    mock_status.assert_called_once_with("TestService")


def test_start_returns_false_when_start_command_fails():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        return_value="Stopped",
    ), patch.object(
        controller,
        "_run_sc",
        return_value=(False, "error"),
    ):
        assert controller.start("TestService") is False


def test_start_returns_true_for_immediate_running():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        side_effect=["Stopped", "Running"],
    ) as mock_status, patch.object(
        controller,
        "_run_sc",
        return_value=(True, ""),
    ) as mock_run_sc:
        assert controller.start("TestService") is True

    mock_run_sc.assert_called_once_with("start", "TestService")
    assert mock_status.call_count == 2


def test_start_returns_true_for_immediate_start_pending():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        side_effect=["Stopped", "Start Pending"],
    ) as mock_status, patch.object(
        controller,
        "_run_sc",
        return_value=(True, ""),
    ):
        assert controller.start("TestService") is True

    assert mock_status.call_count == 2


def test_start_returns_false_for_non_pending_state():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        side_effect=["Stopped", "Stopped"],
    ), patch.object(
        controller,
        "_run_sc",
        return_value=(True, ""),
    ), patch(
        "services.firebird.service_controller.time.time",
        side_effect=[0, 31],
    ):
        assert controller.start("TestService") is False


def test_stop_returns_true_when_already_stopped():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        return_value="Stopped",
    ) as mock_status:
        assert controller.stop("TestService") is True

    mock_status.assert_called_once_with("TestService")


def test_stop_returns_false_when_stop_command_fails():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        return_value="Running",
    ), patch.object(
        controller,
        "_run_sc",
        return_value=(False, "error"),
    ):
        assert controller.stop("TestService") is False


def test_stop_returns_true_for_immediate_stopped():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        side_effect=["Running", "Stopped"],
    ) as mock_status, patch.object(
        controller,
        "_run_sc",
        return_value=(True, ""),
    ) as mock_run_sc:
        assert controller.stop("TestService") is True

    mock_run_sc.assert_called_once_with("stop", "TestService")
    assert mock_status.call_count == 2


def test_stop_returns_true_for_immediate_stop_pending():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        side_effect=["Running", "Stop Pending"],
    ) as mock_status, patch.object(
        controller,
        "_run_sc",
        return_value=(True, ""),
    ):
        assert controller.stop("TestService") is True

    assert mock_status.call_count == 2


def test_stop_returns_false_for_non_pending_state():
    controller = ServiceController()

    with patch.object(
        controller,
        "status",
        side_effect=["Running", "Running"],
    ), patch.object(
        controller,
        "_run_sc",
        return_value=(True, ""),
    ), patch(
        "services.firebird.service_controller.time.time",
        side_effect=[0, 31],
    ):
        assert controller.stop("TestService") is False


def test_restart_returns_false_when_stop_fails():
    controller = ServiceController()

    with patch.object(
        controller,
        "stop",
        return_value=False,
    ) as mock_stop, patch.object(
        controller,
        "start",
    ) as mock_start:
        assert controller.restart("TestService") is False

    mock_stop.assert_called_once_with("TestService")
    mock_start.assert_not_called()


def test_restart_stops_then_starts_service():
    controller = ServiceController()

    with patch.object(
        controller,
        "stop",
        return_value=True,
    ) as mock_stop, patch.object(
        controller,
        "start",
        return_value=True,
    ) as mock_start:
        assert controller.restart("TestService") is True

    mock_stop.assert_called_once_with("TestService")
    mock_start.assert_called_once_with("TestService")


def test_restart_returns_start_result():
    controller = ServiceController()

    with patch.object(
        controller,
        "stop",
        return_value=True,
    ), patch.object(
        controller,
        "start",
        return_value=False,
    ):
        assert controller.restart("TestService") is False