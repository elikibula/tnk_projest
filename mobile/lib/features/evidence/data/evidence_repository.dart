import 'dart:convert';
import 'dart:io';

import 'package:cryptography/cryptography.dart';
import 'package:drift/drift.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:uuid/uuid.dart';

import '../../../core/auth/auth_models.dart';
import '../../../core/database/app_database.dart';
import '../../../core/database/sync_status.dart';
import '../domain/evidence_models.dart';
import 'evidence_cipher.dart';
import 'evidence_remote_data_source.dart';

class EvidenceRepository {
  EvidenceRepository(this._database, this._remote, this._cipher, {Uuid? uuid})
    : _uuid = uuid ?? const Uuid();
  final AppDatabase _database;
  final EvidenceRemoteDataSource _remote;
  final EvidenceCipher _cipher;
  final Uuid _uuid;

  Future<String> queue({
    required String ownerUuid,
    required String reportLocalUuid,
    required File source,
    required String mediaType,
    required EvidenceMetadata metadata,
    bool compressImage = false,
  }) async {
    final localUuid = _uuid.v4();
    var bytes = await source.readAsBytes();
    if (compressImage && bytes.length > 1024 * 1024) {
      bytes = await FlutterImageCompress.compressWithList(
        bytes,
        minWidth: 2048,
        minHeight: 2048,
        quality: 85,
      );
    }
    final digest = await Sha256().hash(bytes);
    final directory = Directory(
      p.join(
        (await getApplicationSupportDirectory()).path,
        'protected_evidence',
      ),
    );
    await directory.create(recursive: true);
    final protected = File(p.join(directory.path, '$localUuid.enc'));
    await _cipher.encryptToFile(bytes, protected);
    await _database
        .into(_database.pendingAttachments)
        .insert(
          PendingAttachmentsCompanion.insert(
            localUuid: localUuid,
            ownerUserUuid: ownerUuid,
            reportLocalUuid: reportLocalUuid,
            localPath: protected.path,
            mediaType: mediaType,
            checksumSha256: digest.bytes
                .map((value) => value.toRadixString(16).padLeft(2, '0'))
                .join(),
            byteSize: bytes.length,
            syncStatus: SyncStatus.pendingCreate.value,
            createdAt: DateTime.now().toUtc(),
            updatedAt: DateTime.now().toUtc(),
            metadataJson: Value(
              jsonEncode({
                ...metadata.toJson(),
                'filename': p.basename(source.path),
              }),
            ),
            idempotencyKey: Value(localUuid),
          ),
        );
    return localUuid;
  }

  Future<int> syncPending(AuthSession session) async {
    final rows =
        await (_database.select(_database.pendingAttachments)..where(
              (row) =>
                  row.ownerUserUuid.equals(session.user.uuid) &
                  row.syncStatus.isIn([
                    SyncStatus.pendingCreate.value,
                    SyncStatus.failed.value,
                  ]),
            ))
            .get();
    var uploaded = 0;
    for (final row in rows) {
      final report =
          await (_database.select(_database.draftReports)
                ..where((item) => item.localUuid.equals(row.reportLocalUuid)))
              .getSingle();
      if (report.serverUuid == null || row.retryCount >= 4) continue;
      await (_database.update(
        _database.pendingAttachments,
      )..where((item) => item.localUuid.equals(row.localUuid))).write(
        PendingAttachmentsCompanion(
          syncStatus: Value(SyncStatus.uploading.value),
        ),
      );
      try {
        final metadata = jsonDecode(row.metadataJson) as Map<String, dynamic>;
        final filename = metadata.remove('filename').toString();
        final response = await _remote.upload(
          token: session.tokens.accessToken,
          reportUuid: report.serverUuid!,
          idempotencyKey: row.idempotencyKey ?? row.localUuid,
          filename: filename,
          mediaType: row.mediaType,
          bytes: await _cipher.decryptFile(File(row.localPath)),
          metadata: metadata,
        );
        await (_database.update(
          _database.pendingAttachments,
        )..where((item) => item.localUuid.equals(row.localUuid))).write(
          PendingAttachmentsCompanion(
            serverUuid: Value(response['uuid'].toString()),
            syncStatus: Value(SyncStatus.synced.value),
            syncError: const Value(null),
            updatedAt: Value(DateTime.now().toUtc()),
          ),
        );
        await File(row.localPath).delete();
        uploaded++;
      } on EvidenceUploadFailure catch (error) {
        await (_database.update(
          _database.pendingAttachments,
        )..where((item) => item.localUuid.equals(row.localUuid))).write(
          PendingAttachmentsCompanion(
            syncStatus: Value(SyncStatus.failed.value),
            retryCount: Value(error.permanent ? 4 : row.retryCount + 1),
            syncError: Value(
              error.permanent
                  ? 'Evidence was rejected. Review the file and metadata.'
                  : 'Evidence upload failed. Retry synchronization.',
            ),
            updatedAt: Value(DateTime.now().toUtc()),
          ),
        );
      } on Object {
        await (_database.update(
          _database.pendingAttachments,
        )..where((item) => item.localUuid.equals(row.localUuid))).write(
          PendingAttachmentsCompanion(
            syncStatus: Value(SyncStatus.failed.value),
            retryCount: Value(row.retryCount + 1),
            syncError: const Value(
              'Evidence upload failed. Retry synchronization.',
            ),
            updatedAt: Value(DateTime.now().toUtc()),
          ),
        );
      }
    }
    return uploaded;
  }
}
