"""HTTP client for VictoriaLogs and VictoriaTraces queries."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any

import httpx


class ObservabilityClient:
    """Async HTTP client for observability queries."""

    def __init__(self, victorialogs_url: str, victoriatraces_url: str):
        self.victorialogs_url = victorialogs_url.rstrip("/")
        self.victoriatraces_url = victoriatraces_url.rstrip("/")

    @asynccontextmanager
    async def _http_client(self):
        """Context manager for HTTP client."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client

    async def logs_search(
        self,
        query: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search logs using LogsQL query.

        Args:
            query: LogsQL query string (e.g., 'service.name:"backend" severity:ERROR')
            limit: Max number of results to return

        Returns:
            List of log entries as dicts
        """
        async with self._http_client() as client:
            response = await client.get(
                f"{self.victorialogs_url}/select/logsql/query",
                params={"query": query, "limit": limit},
            )
            response.raise_for_status()
            return response.json()

    async def logs_error_count(
        self,
        service_name: str,
        time_range: str = "1h",
    ) -> dict[str, Any]:
        """Count errors per service over a time window.

        Args:
            service_name: Service name to filter (e.g., "Learning Management Service")
            time_range: Time range (e.g., "10m", "1h")

        Returns:
            Dict with error count and details
        """
        query = f'_time:{time_range} service.name:"{service_name}" severity:ERROR'
        logs = await self.logs_search(query, limit=1000)
        return {
            "service_name": service_name,
            "time_range": time_range,
            "error_count": len(logs),
            "recent_errors": logs[:10],
        }

    async def traces_list(
        self,
        service_name: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """List recent traces for a service.

        Args:
            service_name: Service name to filter
            limit: Max number of traces to return

        Returns:
            List of trace objects
        """
        async with self._http_client() as client:
            response = await client.get(
                f"{self.victoriatraces_url}/select/jaeger/api/traces",
                params={"service": service_name, "limit": limit},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])

    async def traces_get(
        self,
        trace_id: str,
    ) -> dict[str, Any] | None:
        """Fetch a specific trace by ID.

        Args:
            trace_id: Trace ID (typically from logs)

        Returns:
            Trace object with spans, or None if not found
        """
        async with self._http_client() as client:
            response = await client.get(
                f"{self.victoriatraces_url}/select/jaeger/api/traces/{trace_id}",
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return data.get("data", [{}])[0] if data.get("data") else None
