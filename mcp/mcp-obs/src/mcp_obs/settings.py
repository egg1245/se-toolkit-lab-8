"""Settings for observability MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ObservabilitySettings:
    """Configuration for VictoriaLogs and VictoriaTraces endpoints."""

    victorialogs_url: str
    victoriatraces_url: str


def resolve_settings(
    victorialogs_url: str | None = None,
    victoriatraces_url: str | None = None,
) -> ObservabilitySettings:
    """Resolve observability settings from arguments or environment variables."""
    return ObservabilitySettings(
        victorialogs_url=victorialogs_url
        or os.environ.get("NANOBOT_VICTORIALOGS_URL", "http://localhost:9428"),
        victoriatraces_url=victoriatraces_url
        or os.environ.get("NANOBOT_VICTORIATRACES_URL", "http://localhost:10428"),
    )
