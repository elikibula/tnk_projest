# Production and staging deployment

## Required environment

Use an approved secrets manager or a root-readable environment file outside the repository. Start from `.env.example`, replace every placeholder, and set at minimum:

- a long random `DJANGO_SECRET_KEY`;
- a password-protected PostgreSQL `DATABASE_URL`;
- exact `DJANGO_ALLOWED_HOSTS` and HTTPS `DJANGO_CSRF_TRUSTED_ORIGINS`;
- `DJANGO_SECURE_SSL_REDIRECT=True` after TLS forwarding is verified;
- persistent `DJANGO_MEDIA_ROOT` and `DJANGO_STATIC_ROOT` paths;
- optional `SENTRY_DSN`, environment, release, and sampling rate.

Production settings reject an absent/placeholder secret and incomplete or non-PostgreSQL database URL. `DEBUG` remains false. Database persistent connections use health checks.

## Static assets

Production does not use the Tailwind browser CDN. The pinned Tailwind 3.4.17 standalone compiler builds `backend/static/css/tailwind.css`; the compiler checksum is verified before execution.

On Windows development hosts:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\build-css.ps1
```

The Docker asset stage downloads the pinned Linux compiler, verifies its SHA-256 checksum, and builds the same stylesheet before the Python image is assembled. Rebuild CSS whenever template utility classes change. `collectstatic` then gathers the generated stylesheet and application JavaScript. Nginx gives versioned static assets a one-year immutable cache policy.

## Docker staging procedure

Docker remained unavailable during the R6 validation on 13 August 2026. Static
configuration and production `collectstatic` checks passed after fixing fresh
named-volume ownership and adding a strict `.dockerignore`, but runtime and TLS
checks remain mandatory on the actual staging host:

```powershell
docker compose config
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs --no-log-prefix web nginx db
```

Verify the database and web health checks, `/healthz/`, migrations, static CSS/JS through Nginx, and a normal login. Confirm `/media/anything` returns 404. Confirm the container environment has `DEBUG=False`, Gunicorn is the web process, secrets are not image layers or log output, and named database/media volumes persist after `docker compose restart`.

The bundled Nginx listener is HTTP and is intended to sit behind an approved TLS load balancer/reverse proxy. It preserves an incoming `X-Forwarded-Proto` header. Do not enable secure redirect until that proxy supplies `https`; do not disable secure redirect in a live TLS deployment. TLS certificates, DNS, encrypted storage volumes, firewall rules, and log transport are infrastructure responsibilities.

## Security headers

Django sends a Content Security Policy that defaults scripts to self plus the currently approved Chart.js/Leaflet origins, images to self/data plus OpenStreetMap tiles, blocks objects and framing, and limits forms/base URLs to self. Inline executable scripts were removed; inline style remains allowed only because report progress widths are currently rendered as style attributes. Django also sends Permissions Policy, nosniff, referrer, and frame protections. Review the CSP before changing external map/chart providers.

## Health and monitoring

`/healthz/` performs a database query and returns only `{"status":"ok"}` or a 503 result. It requires no authentication and exposes no version, hostname, or database detail. Monitor it externally and alert on consecutive failures.

Production logs are JSON on stdout with an allow-list of operational fields. Request IDs are returned in `X-Request-ID`. Server errors, rejected workflow operations, validation issues, export failures, and denied evidence access have dedicated logger/event names. Logs intentionally exclude passwords, tokens, request bodies, query strings, document content, health detail, and user identity.

Sentry is optional and environment-configured. It has default PII collection disabled and strips user, body, cookies, authorization, CSRF, and cookie headers before sending. Configure release identifiers and alert routing in staging before production. Apply approved retention and access policies to both ordinary logs and Sentry.

## Release checklist

1. Build assets and application image from a tagged revision.
2. Run `manage.py check --deploy`, migration drift, tests, and dependency/security scans.
3. Back up the database and protected media; verify manifest checksums.
4. Apply migrations once, collect static files, and seed governed reference data idempotently.
5. Start services, verify health/static/media denial/login/workflow/export, then restart and verify persistence.
6. Monitor errors and latency during the controlled release window; retain a tested rollback image and restore procedure.
