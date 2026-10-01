# Record photo evidence

The website supports photos on records in Agriculture and food security,
IVDP projects, Housing and village assets, Water, and Climate and disaster
preparedness. Agriculture photos attach to crop-production or food-security
records; this does not introduce individual farm records.

Save a record, open **Photo evidence** beside it, and add up to ten photos per
submission. Each photo has its own caption, actual capture date/time (Fiji local
time), Observation/Before/Progress/After label, confidentiality level, and optional
GPS coordinates. More photos can be added in later submissions. GPS is requested
only by clicking **Use current GPS**; HTTPS or localhost is required by browsers.
The current device location should only be used at the photographed location.

JPG/JPEG and PNG files are decoded and validated, including the configured
`TNK_MAX_UPLOAD_BYTES` limit (10 MiB by default). Original files retain embedded
metadata; remove sensitive EXIF data before uploading. Thumbnail and enlarged
previews omit embedded metadata. Gallery, preview and original-download responses
are private and are not cached. Files are never linked by public media URL.

`RecordPhoto` links a protected `EvidenceDocument` to a report, section, entry
type and stable record identifier. Report-level evidence lists also include these
documents. Existing workflow, village, role, section and confidentiality rules
apply. Uploads are blocked after submission; authorised users can still view
photos. Photos do not automatically verify quantities, complete records or change
section progress. Failed batches roll back database writes and remove files from
that upload attempt. Existing unrelated files are untouched.

Deployment: run `python manage.py migrate`, collect static assets using the normal
deployment procedure, and restart the application. Migration:
`documents.0003_recordphoto`. No changes to legacy direct file fields.

This implementation covers website cards. The Flutter app's existing report-level
camera/gallery evidence workflow remains unchanged.

## Photo Reports for senior officers

The dashboard and desktop/mobile website menus include **Photo Reports** for
active Roko Tui Veivuke, Roko Tui, Provincial Administrator and System Administrator
roles (and superusers). Other roles cannot access these routes directly.

Use province, tikina, village, year and quarter filters to select a report, then
review its image gallery. Location options and reports remain within the user's
assignments. The gallery includes JPG/JPEG/PNG evidence from both record uploads
and the general report Evidence section; it does not include PDFs or office files.
Area and stage filters, stage grouping, pagination, an enlarged-image dialog,
caption/capture date/GPS details, and links back to the related record are provided.
Older general photos display "Not specified" for stage and "Not recorded" when
there is no capture timestamp; upload time is not presented as capture time.

Photo counts include only images the viewer may access. Draft, returned and
ready-for-validation evidence retains its existing restrictions: senior review
roles alone do not grant access to pre-submission evidence. The gallery is
read-only and does not verify or change report data. No additional migration is
required for the Photo Reports menu/gallery feature.
