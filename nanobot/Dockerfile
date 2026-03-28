ARG REGISTRY_PREFIX_DOCKER_HUB=

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.12-slim

WORKDIR /app

# Install project dependencies directly with pip from workspace
COPY --from=workspace . /build
COPY --from=workspace nanobot-websocket-channel /build/nanobot-websocket-channel

WORKDIR /build

# Install local MCP packages FIRST (so they're available during nanobot build)
RUN pip install --no-cache-dir -e /build/mcp/mcp-lms \
  && pip install --no-cache-dir -e /build/mcp/mcp-obs

# Install nanobot-channel-protocol and nanobot-webchat from subdirectories
RUN pip install --no-cache-dir \
    /build/nanobot-websocket-channel/nanobot-channel-protocol \
    /build/nanobot-websocket-channel/nanobot-webchat

# Install nanobot-ai and nanobot-agent
RUN pip install --no-cache-dir nanobot-ai \
  && pip install --no-cache-dir -e /build/nanobot

# Copy config and entrypoint
WORKDIR /app
COPY config.json /app/agent-config.json
COPY workspace/ /app/agent-workspace/
RUN chmod -R 777 /app/agent-workspace
COPY entrypoint.py /app/entrypoint.py
COPY --from=workspace mcp ./mcp/

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/bin/bash", "-c", "python /app/entrypoint.py"]
