# Backup and restore

Target RPO: 24 hours. Target RTO: 8 hours, subject to infrastructure approval. Run daily encrypted PostgreSQL custom-format backups and protected-media backups, retain 30 daily and 12 monthly copies, and keep encryption keys separately from backup objects.

## Backup

Set `DATABASE_URL` without printing it, then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\backup-postgres.ps1 -OutputFile D:\approved-backups\tnk.dump
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\backup-media.ps1 -MediaRoot D:\tnk-media -OutputFile D:\approved-backups\tnk-media.zip
```

The scripts fail on command errors and print SHA-256 checksums. Record those checksums with application version, schema migration state, timestamp, operator, database backup size, media backup size, encryption/key identifier, and storage location. The scripts do not encrypt or transfer files; approved infrastructure must encrypt them before off-site storage.

## Restore rehearsal

Restore only into new, empty infrastructure. The database restore script refuses targets whose database name does not contain `stage`, `staging`, `rehearsal`, or `test`. The media restore script refuses a non-empty target.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\restore-postgres.ps1 -BackupFile D:\approved-backups\tnk.dump -TargetDatabaseUrl $stagingDatabaseUrl
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\restore-media.ps1 -BackupFile D:\approved-backups\tnk-media.zip -TargetDirectory D:\tnk-media-restored
```

Run migrations, `manage.py check --deploy`, and the guarded fictional/verification command. The command requires PostgreSQL, `TNK_ALLOW_STAGING_REHEARSAL=true`, and a clearly named staging/rehearsal/test database:

```powershell
python backend\manage.py staging_rehearsal --verify-only
```

Compare users, roles, reports, approved status, indicator rows, export audits, and evidence checksums. Start a new application process and restart PostgreSQL/container services, then repeat verification. Never use `staging_rehearsal` on production or a database containing TNK reports.

See `docs/staging-restore-rehearsal.md` for the Phase H evidence. Perform and record a quarterly staging restore. Test key access, off-site retrieval, alerts, retention expiry, and recovery personnel—not only file creation.
