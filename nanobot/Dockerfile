ARG REGISTRY_PREFIX_DOCKER_HUB=

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.12-slim

WORKDIR /app

# Install project dependencies directly with pip from workspace
COPY --from=workspace . /build

WORKDIR /build

# Copy nanobot-websocket-channel first (needed for install)
RUN [ -d /build/nanobot-websocket-channel ] || echo "nanobot-websocket-channel not found in workspace"

# Install local MCP packages FIRST (so they're available during nanobot build)
RUN pip install --no-cache-dir -e /build/mcp/mcp-lms \
  && pip install --no-cache-dir -e /build/mcp/mcp-obs

# Only install webchat packages if they exist
RUN if [ -d /build/nanobot-websocket-channel/mcp-webchat ]; then \
  pip install --no-cache-dir -e /build/nanobot-websocket-channel/mcp-webchat; \
  fi
RUN if [ -d /build/nanobot-websocket-channel/nanobot-webchat ]; then \
  pip install --no-cache-dir -e /build/nanobot-websocket-channel/nanobot-webchat; \
  fi

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

# Copy nanobot-websocket-channel if it exists (for webchat)
COPY --from=workspace nanobot-websocket-channel ./nanobot-websocket-channel/

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/bin/bash", "-c", "python /app/entrypoint.py"]
