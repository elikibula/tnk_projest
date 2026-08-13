FROM debian:bookworm-slim AS assets
WORKDIR /build
ARG TAILWIND_VERSION=3.4.17
ARG TAILWIND_SHA256=7d24f7fa191d2193b78cd5f5a42a6093e14409521908529f42d80b11fde1f1d4
RUN --mount=type=secret,id=build_ca,required=false \
    apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates wget \
    && if [ -s /run/secrets/build_ca ]; then \
         cp /run/secrets/build_ca /usr/local/share/ca-certificates/tnk-build-ca.crt; \
         update-ca-certificates; \
       fi \
    && wget -q "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-x64" -O /usr/local/bin/tailwindcss \
    && echo "${TAILWIND_SHA256}  /usr/local/bin/tailwindcss" | sha256sum -c - \
    && chmod 755 /usr/local/bin/tailwindcss
COPY tailwind.config.js ./
COPY frontend ./frontend
COPY backend/templates ./backend/templates
RUN mkdir -p backend/static/css \
    && tailwindcss -c tailwind.config.js -i frontend/tailwind.css -o backend/static/css/tailwind.css --minify

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN --mount=type=secret,id=build_ca,required=false \
    apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates fonts-dejavu-core \
    && if [ -s /run/secrets/build_ca ]; then \
         cp /run/secrets/build_ca /usr/local/share/ca-certificates/tnk-build-ca.crt; \
         update-ca-certificates; \
       fi \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -f /usr/local/share/ca-certificates/tnk-build-ca.crt \
    && update-ca-certificates
COPY backend /app
COPY --from=assets /build/backend/static/css/tailwind.css /app/static/css/tailwind.css
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh \
    && adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app
USER appuser
ENTRYPOINT ["/entrypoint.sh"]
