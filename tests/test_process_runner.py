import subprocess
from unittest.mock import MagicMock, patch

from core.process_runner import ProcessRunner, ProcessResult


def test_process_result_defaults():
    result = ProcessResult(success=True)

    assert result.success is True
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.return_code == 0
    assert result.duration == 0.0


def test_process_runner_success():
    runner = ProcessRunner()

    with patch("core.process_runner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="TEST OK\n",
            stderr="",
        )

        result = runner.run(
            ["cmd", "/c", "echo", "TEST OK"],
            log_operation=False,
        )

    assert result.success is True
    assert result.stdout == "TEST OK"
    assert result.stderr == ""
    assert result.return_code == 0
    assert result.duration >= 0


def test_process_runner_failure_uses_stderr():
    runner = ProcessRunner()

    with patch("core.process_runner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Błąd procesu\n",
        )

        result = runner.run(
            ["cmd", "/c", "test"],
            log_operation=False,
        )

    assert result.success is False
    assert result.stdout == ""
    assert result.stderr == "Błąd procesu"
    assert result.return_code == 1


def test_process_runner_failure_uses_stdout_when_stderr_empty():
    runner = ProcessRunner()

    with patch("core.process_runner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Błąd stdout\n",
            stderr="",
        )

        result = runner.run(
            ["cmd", "/c", "test"],
            log_operation=False,
        )

    assert result.success is False
    assert result.stderr == ""
    assert result.stdout == "Błąd stdout"
    assert result.return_code == 1


def test_process_runner_timeout():
    runner = ProcessRunner()

    with patch(
        "core.process_runner.subprocess.run",
        side_effect=subprocess.TimeoutExpired(
            cmd=["cmd", "/c", "test"],
            timeout=10,
        ),
    ):
        result = runner.run(
            ["cmd", "/c", "test"],
            timeout=10,
            log_operation=False,
        )

    assert result.success is False
    assert result.stderr == "Przekroczono czas wykonywania procesu."
    assert result.return_code == -1
    assert result.duration >= 0


def test_process_runner_exception():
    runner = ProcessRunner()

    with patch(
        "core.process_runner.subprocess.run",
        side_effect=RuntimeError("Błąd uruchamiania"),
    ):
        result = runner.run(
            ["cmd", "/c", "test"],
            log_operation=False,
        )

    assert result.success is False
    assert result.stderr == "Błąd uruchamiania"
    assert result.return_code == -1
    assert result.duration >= 0


def test_process_runner_passes_arguments_to_subprocess():
    runner = ProcessRunner()

    with patch("core.process_runner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="OK",
            stderr="",
        )

        runner.run(
            ["cmd", "/c", "echo", "TEST"],
            input_text="INPUT",
            timeout=123,
            log_operation=False,
        )

    mock_run.assert_called_once_with(
        ["cmd", "/c", "echo", "TEST"],
        input="INPUT",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=123,
    )


def test_process_runner_logs_start_and_success():
    runner = ProcessRunner()
    runner.logger = MagicMock()

    with patch("core.process_runner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="OK",
            stderr="",
        )

        runner.run(
            ["cmd", "/c", "test"],
            operation="BACKUP",
        )

    assert runner.logger.log.call_count == 2
    runner.logger.log.assert_any_call(
        "BACKUP",
        True,
        "START",
    )


def test_process_runner_logs_failure():
    runner = ProcessRunner()
    runner.logger = MagicMock()

    with patch("core.process_runner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Błąd",
        )

        runner.run(
            ["cmd", "/c", "test"],
            operation="BACKUP",
        )

    assert runner.logger.log.call_count == 2
    runner.logger.log.assert_any_call(
        "BACKUP",
        False,
        "czas: 0.00 s | Błąd",
    )


def test_process_runner_can_disable_logging():
    runner = ProcessRunner()
    runner.logger = MagicMock()

    with patch("core.process_runner.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="OK",
            stderr="",
        )

        runner.run(
            ["cmd", "/c", "test"],
            log_operation=False,
        )

    runner.logger.log.assert_not_called()