ARG REGISTRY_PREFIX_DOCKER_HUB=

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.12-slim

WORKDIR /build

# Copy everything from workspace root
COPY --from=workspace . .

# Check what we have
RUN ls -la nanobot-websocket-channel/nanobot-channel-protocol/ 2>&1 | head -5 || echo "NOT FOUND!"

# Install local MCP packages FIRST (so they're available during nanobot build)
RUN pip install --no-cache-dir -e ./mcp/mcp-lms \
  && pip install --no-cache-dir -e ./mcp/mcp-obs

# Install nanobot-channel-protocol and nanobot-webchat
# Since they're local projects with pyproject.toml, use direct paths
RUN cd nanobot-websocket-channel/nanobot-channel-protocol && pip install --no-cache-dir -e . && cd /build && \
    cd nanobot-websocket-channel/nanobot-webchat && pip install --no-cache-dir -e . && cd /build

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
