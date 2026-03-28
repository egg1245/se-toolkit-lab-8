ARG REGISTRY_PREFIX_DOCKER_HUB=

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.12-slim

WORKDIR /build

# Copy workspace root with all subdirectories
COPY --from=workspace . .

# Verify all directories are present
RUN ls -la . | head -20 && echo "---" && ls -la nanobot-websocket-channel/ 2>&1 | head -10

# Install local MCP packages FIRST (so they're available during nanobot build)
RUN pip install --no-cache-dir -e ./mcp/mcp-lms \
  && pip install --no-cache-dir -e ./mcp/mcp-obs

# Install nanobot-channel-protocol and nanobot-webchat from subdirectories
RUN pip install --no-cache-dir \
    ./nanobot-websocket-channel/nanobot-channel-protocol \
    ./nanobot-websocket-channel/nanobot-webchat

# Install nanobot-ai and nanobot-agent
RUN pip install --no-cache-dir nanobot-ai \
  && pip install --no-cache-dir -e ./nanobot

# Copy config and entrypoint
WORKDIR /app
COPY --from=workspace nanobot/config.json /app/agent-config.json
COPY --from=workspace nanobot/workspace/ /app/agent-workspace/
RUN chmod -R 777 /app/agent-workspace
COPY --from=workspace nanobot/entrypoint.py /app/entrypoint.py
COPY --from=workspace mcp ./mcp/

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/bin/bash", "-c", "python /app/entrypoint.py"]
