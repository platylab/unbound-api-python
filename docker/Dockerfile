# Build Phase
FROM python:3.13-alpine AS builder

RUN pip install poetry

COPY pyproject.toml poetry.lock README.md /app/
COPY src /app/src/

WORKDIR /app

RUN poetry build

# Runner
FROM python:3.13-alpine AS runner

COPY --from=builder /app/dist/*.whl /app/dist/
RUN apk add --no-cache unbound

ENV APPUSER_UID=1000
RUN adduser -D -u $APPUSER_UID app && chown -R app:app /app &&\
    mkdir -p /usr/local/unbound/server.d/

USER app
WORKDIR /app
ENV TZ=Europe/Paris \
    PATH="/home/app/.local/bin:$PATH"

RUN pip install /app/dist/*.whl

CMD ["unbound-api"]
