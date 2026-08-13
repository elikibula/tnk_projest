# Phase 1 - Foundation

## Scope and plan

1. Establish the standalone monorepo and environment-specific settings.
2. Configure Docker, Gunicorn, Nginx and PostgreSQL.
3. Create the custom user before first project migration.
4. Add roles, role assignments, Province/Tikina/Village, and exclusive location assignments.
5. Add reusable location-scoped village selection.
6. Provide login/logout, protected dashboard and bilingual-ready base layout.
7. Add append-only audit event infrastructure and admin protections.
8. Generate migrations and test constraints, scope and authentication.

## Commands

Install: `pip install -r backend/requirements/development.txt`
Create migrations: `python backend/manage.py makemigrations accounts locations audit`
Migrate: `python backend/manage.py migrate`
Test: `pytest` (or dependency-light `python backend/manage.py test backend.tests`)
Verify: `python backend/manage.py check`, sign in at `/accounts/login/`, and inspect scoped objects through admin.

## Decisions

Location assignment uses three nullable foreign keys plus a database check constraint; this keeps referential integrity across a polymorphic scope. UUID is the external identity while Django integer primary keys remain internal in Phase 1. Role codes are stable machine values. Audit events are append-only in admin. Production refuses to start without `DATABASE_URL`; local/test settings use SQLite only for lightweight development and tests.

## Legacy template

The 2020-2021 TNK PDF is treated as a domain-discovery source, not as a database schema or a single web form. Its detailed visual mapping belongs with the reporting-section design in Phase 2; the architecture already separates master, movement, operational and snapshot data so repeated paper fields are not blindly duplicated.
