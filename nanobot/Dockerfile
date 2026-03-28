ARG REGISTRY_PREFIX_DOCKER_HUB=

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.12-slim

WORKDIR /build

# Copy workspace root (excluding .git to reduce size)
COPY --from=workspace . .

# Install git, clone submodule properly, and install all Python packages
RUN apt-get update && apt-get install -y --no-install-recommends git && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf nanobot-websocket-channel && \
  git clone --depth 1 --recurse-submodules https://github.com/egg1245/se-toolkit-lab-8.git /tmp/repo && \
  cp -r /tmp/repo/nanobot-websocket-channel /build/ && \
  rm -rf /tmp/repo && \
  pip install --no-cache-dir -e ./mcp/mcp-lms && \
  pip install --no-cache-dir -e ./mcp/mcp-obs && \
  pip install --no-cache-dir --ignore-requires-python -e ./nanobot-websocket-channel/nanobot-channel-protocol && \
  pip install --no-cache-dir --ignore-requires-python -e ./nanobot-websocket-channel/nanobot-webchat && \
  pip install --no-cache-dir nanobot-ai && \
  pip install --no-cache-dir -e ./nanobot

# Copy config and entrypoint
WORKDIR /app
COPY --from=workspace nanobot/config.json /app/agent-config.json
COPY --from=workspace nanobot/workspace/ /app/agent-workspace/
RUN chmod -R 777 /app/agent-workspace
COPY --from=workspace nanobot/entrypoint.py /app/entrypoint.py
COPY --from=workspace mcp ./mcp/

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/bin/bash", "-c", "python /app/entrypoint.py"]
