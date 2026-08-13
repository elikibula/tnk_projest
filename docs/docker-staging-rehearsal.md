# Docker, Gunicorn, Nginx and TLS rehearsal — R6

Date: 13 August 2026 (Pacific/Fiji)

Status: **LOCAL RUNTIME PASS WITH FIXES; EXTERNAL STAGING TLS NOT AVAILABLE**

## Environment result

- Docker Desktop: installed successfully in recommended per-user mode
- Docker Desktop version: `4.86.0.236216`
- Installer source: Docker's official Windows x86-64 download
- Installer Authenticode status: valid; signer `Docker Inc`
- Installer SHA-256: `820438E75C16E44B393079154BEA7D27958A15845C23A635B1A1F6F586B2ED44`
- WSL optional feature: enabled successfully by DISM
- Modern WSL runtime: 2.7.11.0; kernel 6.18.33.2-2
- WSL MSI Authenticode status: valid; signer `Microsoft Corporation`
- WSL MSI SHA-256: `A611DDACEE689D2FB1FB5319E58AF7F3998864D86CDCE632EADD8E61614A0F9D`
- Virtual Machine Platform: enabled successfully in the follow-up servicing pass
- Windows restarted after feature activation; no servicing reboot remains pending
- `docker --version`: PASS — Docker 29.7.2 (build `a7dcaa6`)
- `docker compose version`: PASS — Docker Compose v5.3.1
- Docker Engine health: PASS — server 29.7.2
- Ports 80, 443, 8000, 8080 and 8443: no conflicting listener observed

The first combined feature command stopped after the WSL feature returned
success-with-reboot code 3010, before it reached Virtual Machine Platform. After
the first reboot, Docker diagnostics identified this precisely as `Virtual
Machine Platform not enabled` / `No virtualization available`. The missing
feature was enabled successfully and Windows was restarted. WSL now reports
default version 2 and Docker's Linux engine starts correctly.

The Docker Desktop control plane later became unavailable during the first
post-restart persistence probe and recovered after relaunch. A subsequent direct
container start completed the persistence proof successfully.

## Local runtime results

| Check | Result |
| --- | --- |
| Backend multi-stage image build | PASS |
| Tailwind 3.4.17 SHA-256 verification | PASS |
| PostgreSQL 17 startup/health | PASS |
| Fresh migrations | PASS — 54 records |
| Django/Gunicorn health | PASS — `/healthz/` returned 200 JSON |
| Nginx startup and syntax | PASS |
| Static collection/serving | PASS — 158 files; CSS returned 200 |
| Direct protected-media access | PASS — Nginx returned 404 |
| HTTP-to-HTTPS application redirect | PASS — 301 to `https://127.0.0.1/healthz/` |
| Web process identity | PASS — UID 1000 `appuser` |
| Restart policies | PASS — `unless-stopped` on all services |
| `no-new-privileges` | PASS on all services |
| Named-volume pre-restart writes | PASS |
| Full-stack restart | PASS — all containers restarted |
| Post-restart protected-media marker | PASS — `r6-persistence-probe` survived |
| Post-restart static volume | PASS — generated Tailwind CSS survived |
| Post-restart PostgreSQL volume | PASS — all 54 migration records survived |
| Post-restart application health | PASS — database/web healthy; HTTP 200 JSON |

## Static configuration checks

| Check | Result |
| --- | --- |
| Compose YAML parsing | PASS — `db`, `web`, and `nginx` services |
| PostgreSQL named volume | PRESENT |
| Static named volume | PRESENT and read-only in Nginx |
| Protected-media named volume | PRESENT in Django only; not mounted into Nginx |
| Direct `/media/` Nginx access | DENIED by configuration (`404`) |
| Gunicorn production dependency | PASS |
| Entrypoint uses `exec gunicorn` | PASS |
| Entrypoint Linux line endings | PASS |
| Django container runs as non-root user | PASS by configuration |
| `no-new-privileges` | PRESENT on database, web and Nginx services |
| Restart policy | PRESENT on database, web and Nginx services |
| Docker build-context exclusions | PASS after fix |
| Production `collectstatic` | PASS — 158 files copied |
| Required Tailwind/app CSS and JavaScript | PASS |
| Django deployment check | PASS WITH NOTES — six known OpenAPI warnings |

## Defects fixed

1. Fresh `static_data` and `media_data` named volumes could be mounted at paths
   not created/owned by the non-root `appuser`, causing migrations to succeed
   but `collectstatic` or evidence writes to fail. The image now creates and
   owns both mountpoints before switching users.
2. The PostgreSQL service lacked the web/Nginx restart and
   `no-new-privileges` protections. Added both.
3. `.dockerignore` was absent, allowing the full local Flutter SDK, Python
   virtual environment, temporary PostgreSQL clusters, SQLite databases,
   caches, test media and possible signing material into the Docker build
   context. Added strict exclusions.
4. `.env.example` used localhost and an HTTP CSRF origin despite representing
   production settings. Replaced them with a clearly non-live HTTPS staging
   example hostname.
5. Avast Web/Mail Shield intercepts container HTTPS, so GitHub and PyPI failed
   certificate validation. The Dockerfile now accepts an optional BuildKit
   `build_ca` secret, uses it for verified dependency downloads, and removes it
   from the final runtime filesystem after installation. TLS verification was
   never disabled.

## TLS topology

The bundled Nginx service listens on HTTP port 80 and is documented as an
upstream behind an approved TLS load balancer/reverse proxy. No certificate,
private key, staging DNS name or TLS endpoint exists on this host. Therefore:

- HTTPS certificate validation: NOT EXECUTED
- HTTP-to-HTTPS behavior through the real proxy: NOT EXECUTED
- HSTS through the real staging endpoint: NOT EXECUTED
- mobile access to a certificate-valid staging API: NOT EXECUTED

Do not expose this Compose listener directly as a production endpoint. The
staging firewall must restrict upstream access, and the approved proxy must
overwrite forwarding headers rather than trusting public client input.

## Commands required on the real staging host

With a secret-bearing `.env` stored outside source control and an approved TLS
proxy available:

```powershell
docker compose config
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs --no-log-prefix db web nginx
```

Then verify database/web health, `/healthz/`, static CSS/JS, `/media/` denial,
Gunicorn process identity, migrations, login, restart persistence, database and
protected-media volumes, HTTPS redirect, certificate chain, secure cookies and
proxy headers.

Local container runtime and persistence behavior passed. R6 cannot be marked
real-staging/TLS PASS until the approved
hostname, proxy, certificate chain, and post-restart persistence are verified on
the staging host.
