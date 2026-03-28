ARG REGISTRY_PREFIX_DOCKER_HUB=

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.12-slim

WORKDIR /build

# Copy workspace root
COPY --from=workspace . .

# CRITICAL FIX: Gitsubmodules don't get copied via COPY --from=workspace
# Clone nanobot-websocket-channel directly from GitHub if it's empty
RUN if [ ! -d nanobot-websocket-channel/nanobot-webchat/src ] || [ -z "$(ls -A nanobot-websocket-channel/nanobot-webchat/src 2>/dev/null)" ]; then \
  echo "Cloning nanobot-websocket-channel from GitHub..."; \
  rm -rf nanobot-websocket-channel; \
  git clone --depth 1 https://github.com/egg1245/se-toolkit-lab-8.git /tmp/repo && \
  cp -r /tmp/repo/nanobot-websocket-channel /build/ && \
  rm -rf /tmp/repo; \
  fi

# Install local MCP packages FIRST (so they're available during nanobot build)
RUN pip install --no-cache-dir -e ./mcp/mcp-lms \
  && pip install --no-cache-dir -e ./mcp/mcp-obs

# Install nanobot-channel-protocol and nanobot-webchat
RUN pip install --no-cache-dir -e nanobot-websocket-channel/nanobot-channel-protocol && \
    pip install --no-cache-dir -e nanobot-websocket-channel/nanobot-webchat

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
