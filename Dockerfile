ARG PYTHON_VERSION=3.14
ARG DEBIAN_VERSION=trixie

######################
# Install dependencies 
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS builder 

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PYTHON_DOWNLOADS=0
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

WORKDIR /app

RUN uv venv /opt/venv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project


###################
# Application image
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS application
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app
COPY rootfs /

USER nonroot

EXPOSE 8000

WORKDIR /app
ENTRYPOINT ["/entrypoint.sh"]
