from __future__ import annotations

from pathlib import Path

from models.firebird_config import FirebirdConfig


class ConfigService:

    def load(self, config_path: Path | None) -> FirebirdConfig:

        config = FirebirdConfig()

        config.path = config_path
        config.raw = {}

        if config_path is None:
            return config

        if not config_path.exists():
            return config

        config.exists = True

        lines = config_path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            config.raw[key] = value

            key_lower = key.lower()

            if key_lower == "remoteserviceport":

                try:
                    config.remote_service_port = int(value)
                except ValueError:
                    pass

            elif key_lower == "guardian":

                config.guardian = value.lower() in (
                    "1",
                    "true",
                    "yes",
                    "on",
                )

            elif key_lower == "rootdirectory":

                config.root_directory = value

            elif key_lower == "tempdirectories":

                config.temp_directories = value

        return config