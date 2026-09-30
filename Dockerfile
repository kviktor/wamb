ARG PYTHON_VERSION=3.14

######################
# Install dependencies 
FROM python:${PYTHON_VERSION}-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PYTHON_DOWNLOADS=0
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev


###################
# Application image
FROM python:${PYTHON_VERSION}-alpine AS application
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# setup a non-root user
RUN addgroup --system --gid 1000 nonroot \
    && adduser --system --uid 1000 --ingroup nonroot --disabled-password nonroot
USER nonroot

# copy .venv (dependencies) from builder
COPY --from=builder --chown=nonroot:nonroot /app /app
# copy the application
COPY --chown=nonroot:nonroot . /app

WORKDIR /app
RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
