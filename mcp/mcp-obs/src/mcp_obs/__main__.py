"""Entry point for mcp-obs MCP server."""

from mcp_obs.server import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
