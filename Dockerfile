FROM python:3.12-slim AS builder

ARG OFFICECLI_VERSION=v1.0.140
ARG OFFICECLI_FILE=officecli-linux-x64
ARG OFFICECLI_URL=https://github.com/iOfficeAI/OfficeCLI/releases/download/${OFFICECLI_VERSION}/${OFFICECLI_FILE}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -L -o /app/officecli "$OFFICECLI_URL" && \
    chmod +x /app/officecli && \
    apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*


FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir uv && uv pip install --system -e .

COPY --from=builder /app/officecli bin/officecli
COPY . .

RUN mkdir -p output

EXPOSE 8000

ENV OFFICECLI_PATH=bin/officecli
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
