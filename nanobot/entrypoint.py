#!/usr/bin/env python3
"""Entrypoint for nanobot Docker container."""

import json
import os
import sys
from pathlib import Path

# Add venv site-packages to path FIRST
venv_site_packages = "/app/venv/lib/python3.12/site-packages"
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

def main():
    config_path = Path("/app/agent-config.json")
    workspace_path = Path("/app/agent-workspace")
    resolved_config_path = Path("/tmp/config.resolved.json")
    
    # Load and resolve config
    with open(config_path) as f:
        config = json.load(f)
    
    config["providers"]["custom"]["apiKey"] = os.environ.get("LLM_API_KEY", "")
    config["providers"]["custom"]["apiBase"] = os.environ.get("LLM_API_BASE_URL", "")
    config["agents"]["defaults"]["model"] = os.environ.get("LLM_API_MODEL", "coder-model")
    config["gateway"]["host"] = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "0.0.0.0")
    config["gateway"]["port"] = int(os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "18790"))
    
    # Inject webchat channel configuration
    if "channels" not in config:
        config["channels"] = {}
    if "webchat" not in config["channels"]:
        config["channels"]["webchat"] = {
            "enabled": True,
            "allowFrom": ["*"]
        }
    config["channels"]["webchat"]["host"] = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0")
    config["channels"]["webchat"]["port"] = int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8001"))
    config["channels"]["webchat"]["access_key"] = os.environ.get("NANOBOT_ACCESS_KEY", "")
    
    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}
    
    # Configure lms, obs, and webchat MCP servers
    for mcp_name in ["lms", "obs", "webchat"]:
        if mcp_name not in config["tools"]["mcpServers"]:
            config["tools"]["mcpServers"][mcp_name] = {
                "command": "python",
                "args": ["-m", f"mcp_{mcp_name}"]
            }
        if "env" not in config["tools"]["mcpServers"][mcp_name]:
            config["tools"]["mcpServers"][mcp_name]["env"] = {}
    
    config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = os.environ.get("NANOBOT_LMS_BACKEND_URL", "")
    config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = os.environ.get("NANOBOT_LMS_API_KEY", "")
    config["tools"]["mcpServers"]["obs"]["env"]["NANOBOT_VICTORIALOGS_URL"] = os.environ.get("NANOBOT_VICTORIALOGS_URL", "")
    config["tools"]["mcpServers"]["obs"]["env"]["NANOBOT_VICTORIATRACES_URL"] = os.environ.get("NANOBOT_VICTORIATRACES_URL", "")
    
    with open(resolved_config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    # Set sys.argv for nanobot CLI parser
    sys.argv = ["nanobot", "gateway", "--config", str(resolved_config_path), "--workspace", str(workspace_path)]
    
    # Call nanobot CLI
    from nanobot.cli.commands import app
    app()

if __name__ == "__main__":
    main()
