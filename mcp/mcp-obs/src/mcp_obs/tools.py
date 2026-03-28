"""Tool schemas, handlers, and registry for the observability MCP server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_obs.client import ObservabilityClient


class NoArgs(BaseModel):
    """Empty input model for tools that only need server-side configuration."""


class LogsSearchQuery(BaseModel):
    query: str = Field(description="LogsQL query string (e.g., 'service.name:\"backend\" severity:ERROR')")
    limit: int = Field(default=100, ge=1, description="Max results to return (default 100)")


class ErrorCountQuery(BaseModel):
    service_name: str = Field(description="Service name to check (e.g., 'Learning Management Service')")
    time_range: str = Field(
        default="1h",
        description="Time range to check (e.g., '10m', '1h', '24h')"
    )


class TracesListQuery(BaseModel):
    service_name: str = Field(description="Service name to filter traces")
    limit: int = Field(default=20, ge=1, description="Max traces to return (default 20)")


class TracesGetQuery(BaseModel):
    trace_id: str = Field(description="Trace ID (typically from logs)")


ToolPayload = BaseModel | Sequence[BaseModel] | dict
ToolHandler = Callable[[ObservabilityClient, BaseModel], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _logs_search(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require_logs_search_query(args)
    return await client.logs_search(query.query, limit=query.limit)


async def _logs_error_count(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require_error_count_query(args)
    return await client.logs_error_count(query.service_name, time_range=query.time_range)


async def _traces_list(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require_traces_list_query(args)
    return await client.traces_list(query.service_name, limit=query.limit)


async def _traces_get(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = _require_traces_get_query(args)
    trace = await client.traces_get(query.trace_id)
    return trace or {"error": f"Trace {query.trace_id} not found"}


def _require_logs_search_query(args: BaseModel) -> LogsSearchQuery:
    if not isinstance(args, LogsSearchQuery):
        raise TypeError(f"Expected {LogsSearchQuery.__name__}, got {type(args).__name__}")
    return args


def _require_error_count_query(args: BaseModel) -> ErrorCountQuery:
    if not isinstance(args, ErrorCountQuery):
        raise TypeError(f"Expected {ErrorCountQuery.__name__}, got {type(args).__name__}")
    return args


def _require_traces_list_query(args: BaseModel) -> TracesListQuery:
    if not isinstance(args, TracesListQuery):
        raise TypeError(f"Expected {TracesListQuery.__name__}, got {type(args).__name__}")
    return args


def _require_traces_get_query(args: BaseModel) -> TracesGetQuery:
    if not isinstance(args, TracesGetQuery):
        raise TypeError(f"Expected {TracesGetQuery.__name__}, got {type(args).__name__}")
    return args


TOOL_SPECS = (
    ToolSpec(
        "logs_search",
        "Search VictoriaLogs for specific log entries using LogsQL query language. "
        "Useful for finding errors, tracing requests, or understanding what happened at a specific time. "
        "Example: 'service.name:\"backend\" severity:ERROR' or '_time:10m event:db_error'",
        LogsSearchQuery,
        _logs_search,
    ),
    ToolSpec(
        "logs_error_count",
        "Count recent errors in a specific service over a time window. "
        "Returns the number of error-level log entries and examples of recent errors. "
        "Useful for quick health checks: 'Any errors in the backend in the last 10 minutes?'",
        ErrorCountQuery,
        _logs_error_count,
    ),
    ToolSpec(
        "traces_list",
        "List recent distributed traces for a service. Each trace represents one request through the system. "
        "Returns trace IDs and basic metadata. Use this to find the trace ID of a request, "
        "then fetch it with traces_get for detailed span information.",
        TracesListQuery,
        _traces_list,
    ),
    ToolSpec(
        "traces_get",
        "Fetch a specific trace by ID to see the complete request flow across services. "
        "Shows which services handled the request, how long each step took, and where errors occurred. "
        "Trace IDs appear in log entries or can be obtained from traces_list.",
        TracesGetQuery,
        _traces_get,
    ),
)

TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
