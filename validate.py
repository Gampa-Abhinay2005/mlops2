"""Validation utilities for configuration files (TOML & YAML)."""

from __future__ import annotations  # ✅ Enables future annotations (FA100)

from pathlib import Path

import tomllib  # ✅ Built-in TOML parser (Python 3.11+)
import yaml
from pydantic import BaseModel, Field, conint

from logger_setup import logger  # ✅ Move local imports to the bottom (I001)


class ServerConfig(BaseModel):
    """Configuration for a server instance."""

    host: str = Field(..., pattern=r"^\d{1,3}(\.\d{1,3}){3}$")
    port: conint(ge=1024, le=65535)
    workers: conint(ge=1)


class AppConfig(BaseModel):
    """Application configuration with multiple servers."""

    server_1: ServerConfig
    server_2: ServerConfig


def load_and_validate_toml(file_path: str) -> AppConfig | None:
    """Load and validate a TOML configuration file.

    Args:
        file_path (str): Path to the TOML file.

    Returns:
        Optional[AppConfig]: Validated configuration or None on failure.

    """
    try:
        with Path(file_path).open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        logger.error(f"❌ TOML file not found: {file_path}")
        return None
    except tomllib.TOMLDecodeError as e:
        logger.error(f"❌ Invalid TOML format: {e}")
        return None
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Unexpected error while parsing TOML: {e}")
        return None
    else:
        config = AppConfig(**data)  # ✅ Ensure `config` is defined (F821)
        logger.info("✅ TOML is valid: %s", config)
        return config


def load_and_validate_yaml(file_path: str) -> AppConfig | None:
    """Load and validate a YAML configuration file.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        Optional[AppConfig]: Validated configuration or None on failure.

    """
    try:
        with Path(file_path).open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"❌ YAML file not found: {file_path}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"❌ Invalid YAML format: {e}")
        return None
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Unexpected error while parsing YAML: {e}")
        return None
    else:
        config = AppConfig(**data)  # ✅ Ensure `config` is defined (F821)
        logger.info("✅ YAML is valid: %s", config)
        return config


if __name__ == "__main__":
    load_and_validate_toml("config.toml")
    load_and_validate_yaml("config.yaml")
